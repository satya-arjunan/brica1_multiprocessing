import brica1
import time

if __name__ == '__main__':
  n = 1000
  np = 100
  s = brica1.VirtualTimeSyncScheduler(1.0)
  agent = brica1.Agent(s)
  comps = []
  comps.append(brica1.ConstantComponent())
  for i in range(np-2):
    comps.append(brica1.PipeComponent())
  comps.append(brica1.NullComponent())
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
    agent.step()
  print('Latency: ', (time.time() - t0) / (n*2*np) * 1E6, 'microseconds')
  print('Duration/step: ', (time.time() - t0) / (n) * 1E3, 'milliseconds')
  s.end_loop()

