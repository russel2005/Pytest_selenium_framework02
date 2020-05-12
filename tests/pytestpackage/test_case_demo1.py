import pytest


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestOne(object):

    def test_TestOne_mothodA(self):
        print("TestOne mehtod A")

    def test_TestOne_mothodB(self):
        print("TestOne mehtod B")
