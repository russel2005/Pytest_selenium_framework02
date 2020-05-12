import pytest
'''
this conftest run in every method before and after, method level
@pytest.yield_fixture()
def setup():
    print("Running conftest setup")
    yield
    print("Running conftest teardown")
'''

'''
# this will run before and after, each python file, method/function level
@pytest.yield_fixture(scope="module")
def setup():
    print("Running conftest setup")
    yield
    print("Running conftest teardown")
'''
# this will run before and after, each python file,
@pytest.fixture(scope="module")
def setUp():
    print("\nRunning method level setUp")
    yield
    print("\nRunning method level tearDown")


@pytest.fixture(scope="class")
def oneTimeSetUp(browser, osType):
    print("\nRunning one time setUp")
    if browser == 'firefox':
        print("Running tests on FF")
    else:
        print("Running tests on chrome")
    yield
    print("\nRunning one time tearDown")

def pytest_addoption(parser):
    parser.addoption("--browser")
    parser.addoption("--osType", help="Type of operating system")

@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def osType(request):
    return request.config.getoption("--osType")