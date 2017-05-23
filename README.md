# Dilite

[![Build Status](https://travis-ci.org/chetanism/dilite.png)](https://travis-ci.org/chetanism/dilite)

An extremely light weight DI container. The goal is to keep `Dilite` light enough that it seems 
logical to have multiple instances of `Dilite` wired up together in a single application.

## Installation
```shell
pip install dilite
```

## Usage

```python
# import
from dilite.dilite import Dilite

# create an instance
dilite = Dilite()
```

### #service
```python
# #service(<name>, <value>)
dilite.service('a_number', 2)
dilite.service('a_string', 'string')
dilite.service('a_function', lambda x: x * x)
dilite.service('an_instance', SomeClass())
```
Dilite#service is just a wrapper for Dilite#factory. Following two calls are essentially same
```python
dilite.service('some', 'service')
dilite.factory('some', lambda: 'service')
```

### #factory
Specifies a function that is invoked only once to prepare and return a service when it is requested 
the first time. When invoked the function will be passed the dilite#get method that can be used to 
fetch any dependencies from the container.
```python
# #factory(<name>, <factory function>)
dilite.factory('my_fancy_service', lambda c: MyFancyService(c('a_number'), c('a_function')))

def another_service_factory(c):
    fancy_service = c('my_fancy_service')
    fancy_object = fancy_service.do_fancy_stuff()
    return {
        'fancy': fancy_service,
        'stuff': fancy_object
    }
dilite.factory('another_service', another_service_factory);


def some_service_factory(c):
    some_service = SomeService();
    some_service.set_another_service(c('another_service'))
    return some_service    
dilite.factory('some_service', some_service_factory)
```

### #provider
Dilite#provider is another wrapper for Dilite#factory. It is invoked immediately and allows to 
configure returned `factory` method easily.
```python
# #provider(<name>, <function that returns factory function>)

def factory_provider():
    some_thing = do_whatever_fancy_things()
    return lambda c: OneMoreService(some_thing, c('some_service'))
dilite.provider('provides_a_factory', factory_provider)
```

### #get
Gets a service/value from the container.
```python
dilite.service('a_value', 34)
dilite.get('a_value')  # returns 34

dilite.factory('a_service', lambda c: AService(c('a_value')))
dilite.get('a_service')  # returns AService instance

def mailer_factory_provider():
    global ENV
    if ENV == 'test':
        return lambda: TestMailer()
        
    return lambda c: RealMailer(c('config.mailer.username'), c('config.mailer.password'))
    

dilite.provider('mailer', mailer_factory_provider)
dilite.get('mailer')  # returns TestMailer or RealMailer instance depending on value of ENV
```

### #add
Let's you add Dilite instances as child. You can build up a whole tree of Dilite instances. 
Invoking a `get` on any of them will fetch you services defined anywhere in the tree.
Useful to build independent modules with their own `Dilite` instances and then wire them up all 
together at the main app level.
```python
# Each instance would normally be created in it's own module
parent = Dilite()
child1 = Dilite()
child2 = Dilite()
child3 = Dilite()

# A service declared in module `child3`
child3.service('c3.some.service', SomeC3Service())

# Each module will expose their Dilite instance that get added to the parent module
parent.add(child1)
child2.add(child3)
parent.add(child2)
    
# You can fetch the service from any of the dilite instance i.e. all services from all modules are available to each module.
c3_service = parent.get('c3.some.service')
c3_service == child1.get('c3.some.service')
c3_service == child2.get('c3.some.service')
c3_service == child3.get('c3.some.service')
```

### When to use #service and #provider
The #service and #provider methods are just a wrapper around #factory. However, you should take 
care that arguments in `service` call will be evaluated immediately, while any code in `factory` 
will be executed when the service/value is requested the first time.

The following code highlights the difference.
```python
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
```

### License

Copyright © 2015-2016 Chetan Verma, LLC. This source code is licensed under the MIT license found in
the [LICENSE.txt](https://github.com/chetanism/py-dilite/blob/master/LICENSE.txt) file.
license.
