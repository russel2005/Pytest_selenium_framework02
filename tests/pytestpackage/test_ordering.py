'''
pip install pytest-ordering
'''
'''
def test_bar():
    assert True


def test_foo():
    assert True

'''
import pytest

@pytest.mark.run(order=2)
def test_foo():
    assert True

@pytest.mark.run(order=1)
def test_bar():
    assert True

@pytest.mark.run(order=3)
def test_three():
    assert True