import example

s = example.Scheduler(5) #set agent=5
print("agent:", s.get_agent())
s.step()
s.step()
print("agent:", s.get_agent())
s.set_agent(3)
print("agent:", s.get_agent())
s.step()
s.step()
print("agent:", s.get_agent())
