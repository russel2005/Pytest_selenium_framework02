import pytest


@pytest.mark.usefixtures("oneTimeSetUp")
class TestTwo(object):

    def test_TestTwo_mothodA(self, setUp):
        print("TestTwo mehtod A")

    def test_TestTwo_mothodB(self, setUp):
        print("TestTwo mehtod B")
