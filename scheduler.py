import time
import sys
import multiprocessing
size = 2
steps = 10

class Counter(object):
  def __init__(self, initval=0):
    self.val = multiprocessing.RawValue('i', initval)
    self.lock = multiprocessing.Lock()
  def increment(self):
    with self.lock:
      self.val.value += 1
  def value(self):
    with self.lock:
      return self.val.value
  def reset(self):
    with self.lock:
      self.val.value = 0

def step(running, c, a, e1, e2):
  while running.value:
    c.increment()
    e1.wait()
    a[0] = 5
    c.increment()
    e2.wait()

def scheduler_step(running, c, a, e1, e2):
  while c.value() == 0:
    pass
  e2.clear()
  c.reset()
  e1.set();
  while c.value() == 0:
    pass
  print(c.value(), a[0])
  e1.clear()
  c.reset()
  e2.set()

if __name__ == '__main__':
  c = Counter(0)
  running = multiprocessing.Value('i', 1)
  e1 = multiprocessing.Event()
  e2 = multiprocessing.Event()
  a = multiprocessing.Array('i', size)
  p = multiprocessing.Process(target=step, args=(running, c, a, e1, e2))
  p.start()
  for i in range(10):
    scheduler_step(running, c, a, e1, e2)
  e1.set()
  running.value = 0;
  p.join()
