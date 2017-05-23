from dilite.dilite import Dilite
import pytest


class ServiceA:
    pass


class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a


class TestDilite:
    def test_one(self):
        d1 = Dilite()
        d1.service('config.name', 'dilite')
        d1.service('add', lambda x, y: x + y)
        d1.service('service_a', ServiceA())

        d1.factory('service_b', lambda c: ServiceB(c('service_a')))
        d1.factory('simple', lambda c: {'sa': c('service_a'), 'sb': c('service_b')})

        def complex_provider():
            def a_factory(c):
                return {
                    'one': 1,
                    'service_a': c('service_a')
                }
            return a_factory
        d1.provider('complex', complex_provider)

        def add_again():
            d1.service('simple', 1)

        with pytest.raises(ValueError):
            add_again()

        assert isinstance(d1, Dilite)
        assert d1.get('config.name') == 'dilite'

        adder = d1.get('add')
        assert adder(6, 7) == 13

        service_a = d1.get('service_a')
        assert isinstance(service_a, ServiceA)

        service_b = d1.get('service_b')
        assert isinstance(service_b, ServiceB)
        assert isinstance(service_b.service_a, ServiceA)
        assert service_b.service_a == service_a

        simple1 = d1.get('simple')
        simple2 = d1.get('simple')
        assert simple1 == simple2
        assert simple1['sa'] == service_a
        assert simple1['sb'] == service_b

    def test_two(self):
        class Dummy:
            def __init__(self, _id, name):
                self.id = _id
                self.name = name

        counter = 0

        def add_some_services(d, name):
            nonlocal counter
            counter += 1
            d.service('%s.id' % name, counter)
            d.factory('%s.name' % name, lambda: name)
            d.factory('%s.dummy' % name, lambda c: Dummy(c('%s.id' % name), c('%s.name' % name)))

        parent = Dilite()
        child1 = Dilite()
        child2 = Dilite()
        child3 = Dilite()

        add_some_services(parent, 'p')
        add_some_services(child1, 'c1')
        parent.add(child1)
        add_some_services(child2, 'c2')
        child2.add(child3)
        add_some_services(child3, 'c3')
        parent.add(child2)
        child3.factory('c3.spl', lambda c: {
            'p': c('p.name'),
            'c1': c('c1.name'),
        })

        assert parent.get('p.id') == 1
        assert parent.get('c1.id') == 2
        assert parent.get('c2.id') == 3
        assert parent.get('c3.id') == 4

        assert child1.get('p.id') == 1
        assert child2.get('p.id') == 1
        assert child3.get('p.id') == 1

        p_dummy = parent.get('p.dummy')
        assert child1.get('p.dummy') == p_dummy
        assert child2.get('p.dummy') == p_dummy
        assert child3.get('p.dummy') == p_dummy

        assert p_dummy.id == child2.get('p.dummy').id

        c3_spl = child1.get('c3.spl')
        assert c3_spl['p'] == 'p'
        assert c3_spl['c1'] == 'c1'

    def test_three(self):
        dilite = Dilite()
        counter = 1

        def foo():
            nonlocal counter
            counter += 1
            return counter

        dilite.service('a', foo())
        assert dilite.get('a') == 2

        # counter = 3
        foo()

        # foo not yet invoked
        dilite.factory('b', lambda: foo())

        # counter = 4
        foo()

        # foo in factory `b` invoked now
        assert dilite.get('b') == 5

        # counter = 6
        foo()

        # foo() in provider function is invoked immediately
        # v = 7
        def a_provider():
            v = foo()
            return lambda: v

        dilite.provider('c', a_provider)
        assert dilite.get('c') == 7

        # counter = 8
        foo()

        # foo() not called in provider, will be called from factory when requested first time
        dilite.provider('d', lambda: lambda: foo())

        # counter = 9
        foo()

        assert dilite.get('d') == 10
