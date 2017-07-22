import brica1

if __name__ == '__main__':
  s = brica1.VirtualTimeSyncScheduler(1.0)
  agent = brica1.Agent(s)
  n = 10
  comps = []
  comps.append(brica1.ConstantComponent())
  for i in range(n-2):
    comps.append(brica1.PipeComponent())
  comps.append(brica1.NullComponent())
  mod = brica1.Module();
  for i in range(n):
    mod.add_component('c%i'%i, comps[i])
  comps[0].make_out_port('out', 28)
  for i in range(n-1):
    comps[i+1].make_in_port('in', 28)
    comps[i+1].make_out_port('out', 28)
    brica1.connect((comps[i], 'out'), (comps[i+1], 'in'))
  comps[n-1].make_in_port('in', 28)
  brica1.connect((comps[n-2], 'out'), (comps[n-1], 'in'))
  agent.add_submodule('mod', mod)
  s.start_loop()
  for i in range(10):
    agent.step()
  s.end_loop()

