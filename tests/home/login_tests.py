from selenium import webdriver as wd
from selenium.webdriver.common.by import By
class LoginTests():

    def test_validLogin(self):
        baseUrl = "https://the-internet.herokuapp.com/"
        driver = wd.Firefox()
        driver.maximize_window()
        driver.implicitly_wait(3)
        driver.get(baseUrl)

        basic_auth = driver.find_element(By.LINK_TEXT, "Basic Auth")
        basic_auth.click()

