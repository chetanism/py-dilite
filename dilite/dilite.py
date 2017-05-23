from functools import reduce
from inspect import getfullargspec

class Dilite:
    def __init__(self):
        self.factories = {}
        self.services = {}
        self.dilites = []
        self.parent = None

    def factory(self, name, factory):
        if name in self.factories:
            raise ValueError('%s name is already registered' % name)
        self.factories[name] = factory
        return self

    def service(self, name, content):
        return self.factory(name, lambda: content)

    def provider(self, name, provider):
        return self.factory(name, provider())

    def add(self, dilite):
        dilite.parent = self
        self.dilites.append(dilite)

    def get(self, name):
        if self.parent:
            return self.parent.get(name)

        if name in self.services:
            return self.services[name]

        dilite = self.find_dilite_containing(name)
        content = None
        if dilite:
            factory_fn = dilite.factories[name]
            param_count = len(getfullargspec(factory_fn).args)
            if param_count == 0:
                content = factory_fn()
            elif param_count == 1:
                content = factory_fn(self.get)
            else:
                content = factory_fn(self.get, self)
            self.services[name] = content
        return content

    def find_dilite_containing(self, name):
        if name in self.factories:
            return self
        return reduce(lambda found, d: found or d.find_dilite_containing(name), self.dilites, None)
