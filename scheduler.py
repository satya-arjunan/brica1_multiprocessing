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
    c.increment()
    e2.wait()

def scheduler_step(running, c, a, e1, e2, np):
  while c.value() != np:
    pass
  e2.clear()
  c.reset()
  e1.set();
  while c.value() != np:
    pass
  #print(c.value(), a[0])
  e1.clear()
  c.reset()
  e2.set()

if __name__ == '__main__':
  n = 10000
  np = 10
  c = Counter(0)
  running = multiprocessing.Value('i', 1)
  e1 = multiprocessing.Event()
  e2 = multiprocessing.Event()
  a = multiprocessing.Array('i', size)
  procs = [multiprocessing.Process(target=step, args=(running, c, a, e1, e2)) 
          for i in range(np)]
  for p in procs: p.start()
  t0 = time.time()
  for i in range(n):
    scheduler_step(running, c, a, e1, e2, np)
  e1.set()
  running.value = 0;
  print('Latency: ', (time.time() - t0) / (n*2*np) * 1E6, 'microseconds')
  p.join()
