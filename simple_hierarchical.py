import brica1
import time
import random
import numpy

def get_timings(n, np):
  s = brica1.HierarchicalTimeScheduler(1.0)
  agent = brica1.Agent(s)
  comps = []
  comps.append(brica1.ConstantComponent())
  for i in range(np-2):
    comps.append(brica1.PipeComponent())
  comps.append(brica1.NullComponent())
  #exponential
  y = numpy.random.exponential(1.0, np)
  max = numpy.max(y)
  y = y/max*32.0+1
  y = y.astype(int)
  y = numpy.log2(y).astype(int)
  for i in range(np):
    comps[i].set_interval(2**y[i])
  #uniform
  #for c in comps:
  #  interval = 2**random.randint(0,5)
  #  c.set_interval(interval)
  mod = brica1.Module();
  for i in range(np):
    mod.add_component('c%i'%i, comps[i])
  comps[0].make_out_port('out', 28)
  for i in range(np-1):
    comps[i+1].make_in_port('in', 28)
    comps[i+1].make_out_port('out', 28)
    brica1.connect((comps[i], 'out'), (comps[i+1], 'in'))
  comps[np-1].make_in_port('in', 28)
  brica1.connect((comps[np-2], 'out'), (comps[np-1], 'in'))
  agent.add_submodule('mod', mod)
  s.start_loop()
  t0 = time.time()
  for i in range(n):
    #agent.step()
    agent.multiprocessing_step()
  t1 = time.time()
  latency = (t1 - t0) / (n*2*np) * 1E6
  duration = (t1 - t0) / (n) * 1E3
  s.end_loop()
  return latency, duration

if __name__ == '__main__':
  #np = [2, 3, 4]
  np = [2, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 160, 200, 250, 300]
  n = 1000
  print("number of process,", "latency (us),", "duration (ms)")
  for i in np:
    if i > 20:
      n = 100
    latency, duration = get_timings(n, i)
    #print(i, latency, duration/i)
    print latency
