import time
import sys
import multiprocessing
from time import sleep
size = 2
steps = 10

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


def step(running, myid, c, start, end, np):
  while running.value:
    while start.value == 0:
      if not running.value:
        return
    val = c.increment()
    if (val == np):
      c.reset()
      start.value = 0
    while start.value == 1:
      if not running.value:
        return
    val = c.increment()
    if (val == np):
      c.reset()
      end.value = 1

def scheduler_step(running, c, start, end):
  end.value = 0
  start.value = 1
  while end.value == 0:
    pass

if __name__ == '__main__':
  n = 100
  np = 70
  c = Counter(0)
  running = multiprocessing.Value('i', 1)
  start = multiprocessing.RawValue('i', 0)
  end = multiprocessing.RawValue('i', 0)
  procs = [multiprocessing.Process(target=step, args=(running, i, c, start, end, np))
          for i in range(np)]
  for p in procs: p.start()
  t0 = time.time()
  for i in range(n):
    scheduler_step(running, c, start, end)
  end.value = 0
  start.value = 1
  running.value = 0;
  print('Latency: ', (time.time() - t0) / (n*2*np) * 1E6, 'microseconds')
  p.join()
