import pytest
from pytest import *

@fixture(scope='class')
def config(request):
    print("\nconfiguring with %s" % request.param)
    yield
    print("\ncleaning up config")

@fixture(scope='function')
def reset():
    print("\nreseting")

@mark.parametrize("config", ["config-A", "config-B"], indirect=True, scope="class")
@mark.usefixtures("reset")
class TestMoreStuff(object):

    def test_a(self, config):
        print("Method A")

    def test_b(self, config):
        print("Method B")

    def test_c(self, config):
        print("Method C")