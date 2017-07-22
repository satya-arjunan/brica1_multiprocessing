import multiprocessing
from multiprocessing import Value, Process, Pool

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
    def __init__(self, np):
        self.np = np
        self.components = []
        self.counter = Counter(0)
        self.running = multiprocessing.Value('i', 1)
        self.start = multiprocessing.RawValue('i', 0)
        self.end = multiprocessing.RawValue('i', 0)
        for i in range(self.np):
          self.components.append(Component('a%i'%i))
        self.processes = []

    def process_execute(self):
        processes = []
        for c in self.components:
            processes.append(Process(target= c.set_buffer, args = (2,)))
        [p.start() for p in processes]
        [p.join() for p in processes]

    def process_execute2(self):
        processes = []
        for c in self.components:
            processes.append(Process(target= self.do_input, args = (c,)))
        [p.start() for p in processes]
        [p.join() for p in processes]

    def start_loop(self):
        for c in self.components:
            self.processes.append(Process(target= self.loop, args = (c,)))
        [p.start() for p in self.processes]

    def end_loop(self):
        self.end.value = 0
        self.start.value = 1
        self.running.value = 0;
        [p.join() for p in self.processes]

    def do_input(self,component):
        component.set_buffer(2)

    def loop(self, component):
        while self.running.value:
          while self.start.value == 0:
            if not self.running.value:
              return
          val = self.counter.increment()
          if (val == self.np):
            self.counter.reset()
            self.start.value = 0
          while self.start.value == 1:
            if not self.running.value:
              return
          val = self.counter.increment()
          if not self.running.value:
            return
          component.set_buffer(2)
          if (val == self.np):
            self.counter.reset()
            self.end.value = 1

    def step(self):
      self.end.value = 0
      self.start.value = 1
      while self.end.value == 0:
        pass

class Component(object):
    def __init__(self, name):
        self.name = name
        self.buffer = Value('i', 0)
    def set_buffer(self, buffer):
        self.buffer.value = self.buffer.value+buffer

if __name__ == '__main__':
    e = Scheduler(10)
    #e.pool_execute()
    #e.process_execute()
    #e.process_execute2()
    e.start_loop()
    e.step()
    e.step()
    e.step()
    e.step()
    e.step()
    e.step()
    e.end_loop()
    for c in e.components: print c.name, c.buffer.value
