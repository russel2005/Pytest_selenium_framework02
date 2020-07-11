import pytest


test_data = [[1, 2, 2],
             [2, 4, 8],
             [3, 3, 9]]

''' if you want to run parametriza test and require to run one specific method onetime only like setup() method'''
setup = 1


def setup():
    print("this is setup")
    global setup
    setup = 0


@pytest.mark.parametrize("a, b, e", test_data)
def test_mul(a, b, e):
    if setup:
        setup
    assert a*b == e