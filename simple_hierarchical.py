import brica1
import time

def get_timings(n, np):
  s = brica1.HierarchicalTimeScheduler(1.0)
  agent = brica1.Agent(s)
  comps = []
  comps.append(brica1.ConstantComponent())
  for i in range(np-2):
    comps.append(brica1.PipeComponent())
  comps.append(brica1.NullComponent())
  comps[0].set_interval(1)
  comps[1].set_interval(2)
  comps[2].set_interval(2)
  comps[3].set_interval(4)
  comps[4].set_interval(4)
  comps[5].set_interval(8)
  comps[0].set_name('a')
  comps[1].set_name('b')
  comps[2].set_name('c')
  comps[3].set_name('d')
  comps[4].set_name('e')
  comps[5].set_name('f')
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
  np = [6]
  n = 1000
  print("number of process,", "latency (us),", "duration (ms)")
  for i in np:
    if i > 20:
      n = 100
    latency, duration = get_timings(n, i)
    print(i, latency, duration/i)
