# -*- coding: utf-8 -*-

"""
scheduler.py
=====

This module contains the `Scheduler` class which is a base class for various
types of schedulers. The `VirtualTimeSyncScheduler` is implemneted for now.

"""

__all__ = ["Scheduler", "VirtualTimeSyncScheduler", "HierarchicalTimeScheduler", "VirtualTimeScheduler", "RealTimeSyncScheduler"]

from .utils import *

from abc import ABCMeta, abstractmethod
import copy
import time
import numpy

import multiprocessing

class Counter(object):
  def __init__(self, initval=0):
    self.val = multiprocessing.RawValue('i', initval)
    self.lock = multiprocessing.Lock()
  def increment(self):
    with self.lock:
      self.val.value += 1
      return self.val.value
  def value(self):
    return self.val.value
  def reset(self):
    with self.lock:
      self.val.value = 0

class Scheduler(object):
    """
    This class is an abstract class for creating `Scheduler`s. Subclasses must
    override the `step()` method to specify its implementation.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(Scheduler, self).__init__()
        self.num_steps = 0
        self.current_time = multiprocessing.RawValue('d', 0.0)
        self.components = []

    def reset(self):
        self.num_steps = 0
        self.current_time.value = 0.0
        self.components = []

    def update(self, ca):
        print("updating parent")
        self.components = ca.get_all_components()

    def start_loop(self):
        for c in self.components:
            self.processes.append(multiprocessing.Process(target=self.loop,
              args = (c,)))
        [p.start() for p in self.processes]

    def end_loop(self):
        pass

    def loop(self, component):
        pass

    def step(self):
        for component in self.components:
            component.input(self.current_time.value)
        for component in self.components:
            component.fire()
        self.current_time.value = self.current_time.value + self.interval
        for component in self.components:
            component.output(self.current_time.value)
        return self.current_time.value

    @abstractmethod
    def multiprocessing_step(self):
        pass

class VirtualTimeSyncScheduler(Scheduler):
    def __init__(self, interval=1.0):
        super(VirtualTimeSyncScheduler, self).__init__()
        self.interval = interval

    def update(self, ca):
        super(VirtualTimeSyncScheduler, self).update(ca)
        print("updating child")
        self.np = len(self.components)
        self.counter = Counter(0)
        self.event1 = multiprocessing.Event()
        self.event2 = multiprocessing.Event()
        self.running = multiprocessing.Value('i', 1)
        self.start = multiprocessing.RawValue('i', 0)
        self.end = multiprocessing.RawValue('i', 0)
        self.function = multiprocessing.RawValue('i', 0)
        self.processes = []

    def step_processes(self):
        while self.counter.value() != self.np:
          pass
        self.event2.clear()
        self.counter.reset()
        self.event1.set();
        while self.counter.value() != self.np:
          pass
        self.event1.clear()
        self.counter.reset()
        self.event2.set()

    def multiprocessing_step(self):
        self.function.value = 0
        self.step_processes()
        self.function.value = 1
        self.step_processes()
        self.current_time.value = self.current_time.value + self.interval
        #print(self.current_time.value)
        self.function.value = 2
        self.step_processes()
        return self.current_time.value

    def loop(self, component):
        while self.running.value:
          self.counter.increment()
          self.event1.wait()
          if(self.function.value == 0):
            component.input(self.current_time.value)
          elif(self.function.value == 1):
            component.fire()
          else:
            component.output(self.current_time.value)
          self.counter.increment()
          self.event2.wait()

    def end_loop(self):
        self.event1.set()
        self.event2.set()
        self.running.value = 0
        [p.join() for p in self.processes]

class HierarchicalTimeScheduler(Scheduler):
    def __init__(self, interval=1.0):
        super(HierarchicalTimeScheduler, self).__init__()
        self.interval = interval

    def update(self, ca):
        super(HierarchicalTimeScheduler, self).update(ca)
        print("updating child")
        self.running = multiprocessing.Value('i', 1)
        self.curr_time = multiprocessing.RawValue('i', 0)
        self.n = numpy.empty(0, dtype=int)
        self.curr_ni = 0
        self.setup_queue()
        self.setup_events()
        self.curr_time.value = self.interval
        self.processes = []

    def setup_queue(self):
        self.interval = numpy.inf
        for c in self.components:
            if (self.interval > c.interval):
                self.interval = c.interval
        self.interval = int(self.interval)
        for c in self.components:
            c.set_n(self.interval)
            if (c.n not in self.n):
              self.n = numpy.append(self.n, c.n)
        self.n = numpy.sort(self.n)
        self.n_word = 0
        for n in self.n:
          self.n_word = self.n_word + 2**n
        self.np = numpy.zeros(self.n.shape, dtype=int)
        for c in self.components:
          c.set_n_index(numpy.where(self.n == c.n)[0][0])
          for n_index in range(len(self.n)):
            if (2**self.n[n_index] % 2**self.n[c.n_index] == 0):
              self.np[n_index] = self.np[n_index] + 1
        print("np list:", self.np)
        print("n list:",self.n)
        print("n word:",bin(self.n_word))

    def setup_events(self):
        self.events1 = []
        self.events2 = []
        self.counters = []
        for i in range(len(self.n)):
            self.events1.append(multiprocessing.Event())
            self.events2.append(multiprocessing.Event())
            self.counters.append(Counter(0))

    def loop(self, component):
        while self.running.value:
          self.counters[component.curr_ni].increment()
          self.events1[component.curr_ni].wait()
          component.update_next_ni(self.curr_time.value, self.interval,
              self.n_word)
          print("  child:", component.name, component.curr_ni,
              component.next_ni)
          self.counters[component.curr_ni].increment()
          self.events2[component.curr_ni].wait()
          component.update_curr_ni()

    def end_loop(self):
        for i in range(len(self.events1)):
          self.events1[i].set()
          self.events2[i].set()
        self.running.value = 0
        [p.join() for p in self.processes]

    def multiprocessing_step(self):
        self.step_processes()
        self.update_time()
        return self.current_time.value

    def step_processes(self):
        print("parent:",self.curr_ni, "np:", self.np[self.curr_ni],
            "count:", self.counters[self.curr_ni].value(), self.curr_time.value)
        while self.counters[self.curr_ni].value() != self.np[self.curr_ni]:
          pass
        self.events2[self.curr_ni].clear()
        self.counters[self.curr_ni].reset()
        self.events1[self.curr_ni].set();
        while self.counters[self.curr_ni].value() != self.np[self.curr_ni]:
          pass
        self.events1[self.curr_ni].clear()
        self.counters[self.curr_ni].reset()
        self.events2[self.curr_ni].set()

    def update_time(self):
        next_time = self.curr_time.value + self.interval
        a = (next_time^self.curr_time.value)&next_time
        b = (a+a-1)&self.n_word
        self.curr_ni = len(bin(b)[2:])-1 #get MSB
        self.curr_time.value = next_time

class VirtualTimeScheduler(Scheduler):
    """
    `VirtualTimeScheduler` is a `Scheduler` implementation for virutal time.
    """

    class Event(object):
        """
        `Event` is a queue object for `PriorityQueue` in VirtualTimeScheduler.
        """

        def __init__(self, time, component):
            """ Create a new `Event` instance.

            Args:
              time (float): the time of the `Event`.
              component (Component): `Component` to be handled.

            Returns:
              Component: a new `Component` instance.

            """

            super(VirtualTimeScheduler.Event, self).__init__()
            self.time = time
            self.component = component

        def __lt__(self, other):
            return self.time < other.time;

    def __init__(self):
        """ Create a new `Event` instance.

        Args:
          time (float): the time of the `Event`.
          component (Component): `Component` to be handled.

        Returns:
          Component: a new `Component` instance.

        """

        super(VirtualTimeScheduler, self).__init__()
        self.event_queue = queue.PriorityQueue()

    def update(self, ca):
        """ Update the `Scheduler` for given cognitive architecture (ca)

        Args:
          ca (Agent): a target to update.

        Returns:
          None.

        """

        super(VirtualTimeScheduler, self).update(ca)
        for component in self.components:
            component.input(self.current_time)
            component.fire()
            self.event_queue.put(VirtualTimeScheduler.Event(component.offset + component.last_input_time + component.interval, component))

    def step(self):
        """ Step by the internal interval.

        An event is dequeued and `output()`, `input()`, and `fire()` are called
        for the `Component` of interest.

        Args:
          None.

        Returns:
          float: the current time of the `Scheduler`.

        """

        e = self.event_queue.get()
        self.current_time = e.time
        component = e.component
        component.output(self.current_time)
        component.input(self.current_time)
        component.fire()

        self.event_queue.put(VirtualTimeScheduler.Event(self.current_time + component.interval, component))

        return self.current_time

class RealTimeSyncScheduler(Scheduler):
    """
    `RealTimeSyncScheduler` is a `Scheduler` implementation for real time
    in a synced manner.
    """

    def __init__(self, interval=1.0):
        """ Create a new `RealTimeSyncScheduler` Instance.

        Args:
          interval (float): minimu interval in seconds between input and output of the modules.

        Returns:
          RealTimeSyncScheduler: A new `RealTimeSyncScheduler` instance.

        """

        self.last_input_time = -1.0
        self.last_output_time = -1.0
        self.last_spent = -1.0
        self.last_dt = -1.0

        super(RealTimeSyncScheduler, self).__init__()
        self.set_interval(interval)


    def reset():
        super(RealTimeSyncScheduler, self).reset()
        self.set_interval(1.0)


    def set_interval(self, interval):
        self.interval = float(interval)
        assert self.interval > 0.0

    def step(self):
        """ Step by the internal interval.

        The methods `input()`, `fire()`, and `output()` are synchronously
        called for all components.

        The time when it started calling input() and output() of the 
        components is stored in self.last_input_time and 
        self.last_output_time, respectively.

        self.interval sets the *minimum* interval between the point in
        time when input() is called and when output() is called.
        The actual interval between input() and output() will 
        always be longer than self.interval, although the scheduler
        tries to make the discrepancy minimum.

        When calling fire() of the components takes longer than the
        set interval, calling output() of the components will be 
        later than the scheduled time self.input_time + self.interval.
        In this case, self.lagged will be set True.

        During the execution of this method, it will also set self.last_spent,
        which will be the time spent until all components are fired
        after self.last_input_time is set.

        Args:
          None.

        Returns:
          float: the current time of the `Scheduler`.

        """

        self.last_input_time = current_time()
        self.current_time = self.last_input_time

        for component in self.components:
            component.input(self.last_input_time)

        for component in self.components:
            component.fire()

        self.last_spent = current_time() - self.last_input_time
        last_dt = self.interval - self.last_spent

        self.lagged = False
        if last_dt > 0.0:
            time.sleep(last_dt)
        elif last_dt < 0.0:
            self.lagged = True

        self.last_output_time = current_time()
        self.current_time = self.last_output_time

        for component in self.components:
            component.output(self.last_output_time)

        self.last_output_time = current_time()
        self.current_time = self.last_output_time

        return self.current_time
