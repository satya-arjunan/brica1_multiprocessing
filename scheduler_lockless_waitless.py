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

def step(running, myid, c, a):
  while running.value:
    while a[myid] != 1:
      pass
    a[myid] = 2;

def scheduler_step(running, c, a, np):
  for i in range(np):
    a[i] = 1
  val = True
  while val:
    val = False
    for i in range(np):
      if a[i] == 1:
        val = True
        break

if __name__ == '__main__':
  n = 10000
  np = 10
  c = Counter(0)
  running = multiprocessing.Value('i', 1)
  a = multiprocessing.Array('i', np)
  for i in range(np):
    a[i] = 2;
  procs = [multiprocessing.Process(target=step, args=(running, i, c, a))
          for i in range(np)]
  for p in procs: p.start()
  t0 = time.time()
  for i in range(n):
    scheduler_step(running, c, a, np)
  running.value = 0;
  for i in range(np):
    a[i] = 1
  print('Latency: ', (time.time() - t0) / (n*2*np) * 1E6, 'microseconds')
  p.join()
