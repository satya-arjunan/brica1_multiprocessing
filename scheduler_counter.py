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

def step(running, c, a, c1, c2, np):
  with c1:
    c1.wait()

def scheduler_step(running, a, c1, c2):
  with c1:
    c1.notify_all()

if __name__ == '__main__':
  n = 5
  np = 10
  c = Counter(0)
  running = multiprocessing.Value('i', 1)
  c1 = multiprocessing.Condition()
  c2 = multiprocessing.Condition()
  a = multiprocessing.Array('i', size)
  procs = [multiprocessing.Process(target=step, args=(running, c, a, c1, c2, np))
          for i in range(np)]
  for p in procs: p.start()
  t0 = time.time()
  for i in range(n):
    scheduler_step(running, a, c1, c2)
  running.value = 0;
  c1.notify_all()
  print('Latency: ', (time.time() - t0) / (n*2*np) * 1E6, 'microseconds')
  p.join()
