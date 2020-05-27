from selenium import webdriver
import unittest


class GoogleSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(
            executable_path='C:\\Users\\russe\\PycharmProjects\\Pytest_framework\\drivers\\chromedriver.exe')
        cls.driver.implicitly_wait(10)
        cls.driver.maximize_window()


    def test_search_automationstepbystep(self):
        self.driver.get("https://www.google.com")
        self.driver.find_element_by_name('q').send_keys('Automation step by step')
        self.driver.find_element_by_name("btnK").click()


    def test_search_selenium(self):
        self.driver.get("https://www.google.com")
        self.driver.find_element_by_name('q').send_keys('selenium python')
        self.driver.find_element_by_name("btnK").click()


    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()
        print("test done")

if __name__ == '__main__':
    unittest.main()
