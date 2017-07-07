import multiprocessing as mp
import my
import numpy as np
import time

def testFunc(myid):
  pass

def initProcess(a):
  my.a = a

if __name__ == "__main__":
  n = 1000
  pn = 100
  a = mp.Array('i', pn, lock=False)
  for i in range(pn):
    a[i] = i
  b = np.arange(pn)
  p = mp.Pool(processes=pn, initializer=initProcess,initargs=(a,))
  t0 = time.time()
  for i in range(n):
    p.map(testFunc, b)
  p.close()
  print('Latency: ', (time.time() - t0) / (n*2*pn) * 1E6, 'microseconds')
  p.join()
