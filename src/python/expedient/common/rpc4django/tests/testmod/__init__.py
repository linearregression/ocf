from rpc4django import rpcmethod
import testsubmod

@rpcmethod(signature=['int', 'int', 'int'])
def subtract(a, b):
    return a - b

@rpcmethod(signature=['int', 'int', 'int'], url_ns="some_ns")
def product(a, b):
    return a * b
