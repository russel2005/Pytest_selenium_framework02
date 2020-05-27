from selenium import webdriver


url = "https://www.google.com"
driver = webdriver.Chrome(executable_path='C:\\Users\\russe\\PycharmProjects\\Pytest_framework\\drivers\\chromedriver.exe')
driver.implicitly_wait(10)
driver.maximize_window()
driver.get(url)
driver.find_element_by_name('q').send_keys('Automation step by step')
driver.find_element_by_name("btnK").click()

driver.close()
driver.quit()

print("test done")