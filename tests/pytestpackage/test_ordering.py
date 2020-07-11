'''
pip install pytest-ordering
pip install pytest-dependency
'''

import pytest


class Test():

    @pytest.mark.run(order=2)
    def test_foo(self):
        assert True

    #@pytest.mark.run(order=1)
    @pytest.mark.dependency()
    def test_bar(self):
        assert True

    @pytest.mark.run(order=3)
    def test_three(self):
        assert True

    @pytest.mark.dependency(depends=['Test::test_bar'])
    def test_sample01(self):
        assert True
