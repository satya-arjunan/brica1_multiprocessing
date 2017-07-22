from multiprocessing import Value, Process, Pool

class Scheduler(object):
    def __init__(self, name):
        self.name = name
        self.components = []
        self.components.append(Component('a'))
        self.components.append(Component('b'))
        self.components.append(Component('c'))

    def process_execute(self):
        processes = []
        for c in self.components:
            processes.append(Process(target= c.set_buffer, args = (2,)))
        [p.start() for p in processes]
        [p.join() for p in processes]

    def process_execute2(self):
        processes = []
        for c in self.components:
            processes.append(Process(target= self.do_input, args = (c,)))
        [p.start() for p in processes]
        [p.join() for p in processes]

    def do_input(self,component):
        component.set_buffer(2)

    def pool_execute(self): #doesn't work
        pool = Pool(processes=2)
        print pool.map(self.do_input, self.components)

class Component(object):
    def __init__(self, name):
        self.name = name
        self.buffer = Value('i', 0)
    def set_buffer(self, buffer):
        self.buffer.value = self.buffer.value+buffer

if __name__ == '__main__':
    e = Scheduler('exp')
    #e.pool_execute()
    e.process_execute()
    e.process_execute2()
    for c in e.components: print c.name, c.buffer.value
