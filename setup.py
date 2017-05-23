from distutils.core import setup

setup(
    name='dilite',
    version='0.0.2',
    description='An extremely light weight DI container',
    long_description='An extremely light weight DI container. The goal is to keep Dilite light ' +
                     'enough that it seems logical to have multiple instances of Dilite wired up ' +
                     'together in a single application.',
    url='https://github.com/chetanism/py-dilite',
    author='Chetan Verma',
    author_email='verma.chetan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development'
    ],
    keywords='di ioc dependency-injection dependency injection',
    packages=['dilite']
)
