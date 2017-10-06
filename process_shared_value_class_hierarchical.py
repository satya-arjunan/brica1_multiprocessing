from multiprocessing import Value, Process, Event
import multiprocessing

import numpy
import math


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
    def __init__(self, name):
        self.name = name
        self.components = [] #name, interval, index
        self.components.append(Component('a', 1, 0))
        self.components.append(Component('b', 2, 1))
        self.components.append(Component('c', 4, 2))
        self.components.append(Component('d', 4, 3))
        self.running = multiprocessing.Value('i', 1)
        self.start = multiprocessing.RawValue('i', 0)
        self.end = multiprocessing.RawValue('i', 0)
        self.curr_time = multiprocessing.RawValue('i', 0)
        self.n = numpy.empty(0, dtype=int)
        self.curr_ni = 0
        self.setup_queue()
        self.setup_events()
        self.curr_time.value = self.min_interval

    def setup_events(self):
        self.events1 = []
        self.events2 = []
        self.counters = []
        for i in range(len(self.n)):
            self.events1.append(multiprocessing.Event())
            self.events2.append(multiprocessing.Event())
            self.counters.append(Counter(0))

    def setup_queue(self):
        self.min_interval = numpy.inf
        for c in self.components:
            if (self.min_interval > c.interval):
                self.min_interval = c.interval
        self.min_interval = int(self.min_interval)
        for c in self.components:
            c.set_n(self.min_interval)
            if (c.n not in self.n):
              self.n = numpy.append(self.n, c.n)
        self.n = numpy.sort(self.n)
        self.n_word = 0
        for n in self.n:
          self.n_word = self.n_word + 2**n
        self.np = numpy.zeros(self.n.shape, dtype=int)
        for c in self.components:
          n_index = numpy.where(self.n == c.n)[0][0]
          c.set_n_index(n_index)
          for n_index in range(len(self.n)):
            if ((self.n[c.n_index] == 0) or
                (n_index == c.n_index) or
                ((self.n[n_index] > self.n[c.n_index]) and
                  (self.n[n_index] % self.n[c.n_index] == 0))):
              self.np[n_index] = self.np[n_index] + 1
        print("np list:", self.np)
        print("n list:",self.n)
        print("n word:",bin(self.n_word))

    def process_execute(self):
        self.processes = []
        for c in self.components:
            self.processes.append(Process(target= self.loop, args = (c,)))
        [p.start() for p in self.processes]

    def loop(self, component):
        while self.running.value:
          self.counters[component.curr_ni].increment()
          self.events1[component.curr_ni].wait()
          component.update_next_ni(self.curr_time.value, self.min_interval, self.n_word)
          print("  child:",component.name, component.curr_ni, component.next_ni)
          self.counters[component.curr_ni].increment()
          self.events2[component.curr_ni].wait()
          component.update_curr_ni()

    def end_loop(self):
        for i in range(len(self.events1)):
          self.events1[i].set()
          self.events2[i].set()
        self.running.value = 0
        [p.join() for p in self.processes]

    def step_processes(self):
        print("parent:",self.curr_ni, "np:", self.np[self.curr_ni], "count:", self.counters[self.curr_ni].value(), self.curr_time.value)
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
        self.update_time()

    def update_time(self):
        next_time = self.curr_time.value + self.min_interval
        #print("  next_time:", next_time)
        a = (next_time^self.curr_time.value)&next_time
        #print("  a:", a)
        #print("  n_word:", self.n_word)
        b = (a+a-1)&self.n_word
        #print("  b:", b)
        #print("  bin b:", bin(b).count("1")-1)
        self.curr_ni = len(bin(b)[2:])-1 #get MSB
        self.curr_time.value = next_time


class Component(object):
    def __init__(self, name, interval, index):
        self.name = name
        self.interval = interval
        self.min_interval = 0
        self.index = index
        self.buffer = Value('i', 0)
        self.curr_ni = 0
        self.next_ni = 0

    def set_buffer(self, buffer):
        self.buffer.value = self.buffer.value+buffer

    def set_n(self, min_interval):
        self.n = int(math.log(self.interval/min_interval, 2))

    def set_n_index(self, index):
        self.n_index = index
        self.curr_ni = index

    def update_next_ni(self, curr_time, min_interval, n_word):
        next_time = curr_time + self.interval
        #print("child name:", self.name, "curr_time:", curr_time, "next_time:", next_time)
        a = (next_time^(next_time-min_interval))&next_time
        #print("  name:", self.name, "a:", a)
        b = (a+a-1)&n_word
        #print("  name:", self.name, "b:", b)
        self.next_ni = len(bin(b)[2:])-1 #get MSB

    def update_curr_ni(self):
        self.curr_ni = self.next_ni


if __name__ == '__main__':
    e = Scheduler('exp')
    e.process_execute()
    print("---1")
    e.step_processes()
    print("---2")
    e.step_processes()
    print("---3")
    e.step_processes()
    print("---4")
    e.step_processes()
    print("---5")
    e.step_processes()
    print("---6")
    e.step_processes()
    print("---7")
    e.step_processes()
    print("---8")
    e.step_processes()
    print("---9")
    e.step_processes()
    print("---10")
    e.step_processes()
    print("---11")
    e.step_processes()
    print("---12")
    e.step_processes()
    print("---13")
    e.step_processes()
    print("---14")
    e.step_processes()
    print("---15")
    e.end_loop()
