import os
import random

"""
This module contains UI components for the preview report viewer
"""

from lib.ui.BasePage import BasePage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

class Endpoints(object):
    PAGE_NUM = (By.ID, "page_{}")
    LINE = (By.XPATH, "//div[@data-automation-id='returnPreview-field-{}']")
    LINE_ACTION_MENU = (By.XPATH, "//button[@data-automation-id='returnField-actionMenu-{}-button']")
    LINE_ACTION_CONTAINER = (By.XPATH, "//div[@data-automation-id = 'returnField-actionMenu-{}']/div")
    LINE_ACTION_ITEM = (By.XPATH, "//div[text()='{}']")


class ReturnPreview(BasePage):

    # Initializer
    def __init__(self, driver):
        BasePage.__init__(self, driver)

    # locator
    ZOOM_IN = (By.XPATH, "//button[@type='button']//span[text() = 'Zoom In']")
    ZOOM_OUT = (By.XPATH, "//button[@type='button']//span[text() = 'Zoom Out']")
    ZOOM_DROPDOWN = (By.CSS_SELECTOR, "select.zoom-select")

    def get_zoom_in(self):
        return self.driver.find_element(ReturnPreview.ZOOM_IN)

    def get_zoom_out(self):
        return self.driver.find_element(ReturnPreview.ZOOM_OUT)

    def get_zoom_dropdown(self):
        return self.driver.find_element(ReturnPreview.ZOOM_DROPDOWN)

    def jump_to_page(self, pageNumber):

        """Will enter the given page number in the "Jump to page" text box and click the Go button

        :param pageNumber: Page number (as interger) to enter (Ex: 3)"""

        numBox = self.driver.find_element(By.XPATH, "//input[@class='pagination-input u-margin-left--sm u-margin-right--sm']")
        numBox.click()
        numBox.send_keys(pageNumber)

        self._css_button_click('Go')

    def click_line_item_action_menu(self, lineCode, menu):
        """Will locate and click the Action Menu item of the given line code in the return preview.
        Note - the lineCode for each return preview line item can be found by viewing it's Field Attributes
        :param lineCode:  Line code of the line from the return preview (Ex: LC_2)
        :param menu: Name of Action Menu item to click (Ex: Override Field, View Field Attributes)"""

        # Fine line in preview, click to make action menu button visible
        actionChains = ActionChains(self.driver)
        xpathLine = self._format_tuple(Endpoints.LINE, lineCode)
        line = self.driver.find_element(*xpathLine)
        actionChains.move_to_element(line)
        line.click()

        # Click Action Menu button
        xpathMenu = self._format_tuple(Endpoints.LINE_ACTION_MENU, lineCode)
        actionMenu = line.find_element(*xpathMenu)
        actionChains.move_to_element(actionMenu).perform()
        actionMenu.click()

        # Click action menu item
        xpathItem = self._format_tuple(Endpoints.LINE_ACTION_ITEM, menu)
        menuItem = self.driver.find_element(*xpathItem)
        actionChains.move_to_element(menuItem).perform()
        menuItem.click()

    def click_go_to_page_number(self, pageNumber):

        """Will click on the given page number shown in the bottom right corener of the report preview screen.

        :param pageNumber: Page number as seen in the UI to click (Ex: 2)
        """

        actionChains = ActionChains(self.driver)
        xpath = self._format_tuple(Endpoints.PAGE_NUM, pageNumber)
        pageNum = self.driver.find_element(*xpath)
        actionChains.move_to_element(pageNum).perform()
        actionChains.click(pageNum).perform()

    def verify_report_vaidation_menu_collapsed(self, collapsed='False'):

        """Verifies the Report Validation sub-menu is either collapsed or expanded.
        Initial page load defaults to sub menu expanded, and collpased parameter defualts to false.

        :param collapsed:  Enter boolean value (true for collapsed, false for expanded)"""

        if collapsed.lower() == 'false':
            try:
                menu = self.driver.find_element(By.XPATH,"//div[@class='right-panel__container report-viewer-panel']")
            except NoSuchElementException:
                assert False, "Report validation menu is not expanded as expected"
        elif collapsed.lower() == 'true':
            try:
                menu = self.driver.find_element(By.XPATH,"//div[@class='right-panel__container is-collapsed report-viewer-panel']")
            except NoSuchElementException:
                assert False, "Report validation menu is not collapsed as expected"
        else:
            assert False, "{} is not a valid value for parameter collapsed."

    def verify_return_preview_form_page_num(self, pageNumber):

        """Verifies the page number of the form loaded in the return preview window matches the expected page number.

        :param pageNumber:  Expected page number as an integer (Ex: 1)"""

        expectedNum = ("return-form-image-page_" + pageNumber)

        form = self.driver.find_element(By.XPATH,"//div[@class='report-viewer-inner-container']//img")
        actualNum = form.get_attribute('data-automation-id')

        if actualNum == expectedNum:
            print ("Actual form page number {} equals expected page number {}".format(actualNum, expectedNum))
        else:
            assert False, "Actual form page number {} does not equal expected page number {}".format(actualNum, expectedNum)

    def verify_return_preview_highlighted_page_num(self, pageNumber):

        """Verifies the given page number is the highlighted/active page number outlined at the bottom of the preview screen.

        :param pageNumber:  Expected active/highlighted page number at bottom of screen (Ex: 1, 5, etc.)"""

        expectedNum = ("page_" + pageNumber)
        num = self.driver.find_element(By.XPATH,"//button[@id='{}']".format(expectedNum))
        numStatus = num.get_attribute('class')

        if "transparent" in numStatus:
            assert False, "Page number {} is not highlighted/active as expected".format(pageNumber)

    def verify_return_preview_page_number_text(self, expectedNum):

        """Verifies the given page number is the page number shown in the bottom right corner text box.

        :param pageNumber:  Expected page number shown in the text box (Ex: 1, 5, etc.)"""

        box = self.driver.find_element(By.XPATH, "//input[@class='pagination-input u-margin-left--sm u-margin-right--sm']")
        actualNum = box.get_attribute('value')
        if actualNum == expectedNum:
            print ("Actual page number {} equals expected page number {}".format(actualNum, expectedNum))
        else:
            assert False, "Actual page number {} does not equal expected page number {}".format(actualNum, expectedNum)

    def return_select_action_submenu(self, submenu, reportDownloaded=''):

        """Will select the action menu and then the provided action submenu of the first row in the return list.
        :param submenu:  Name of submenu to select as appears in the UI (Ex: View Tax Data Details)
        :param reportDownloaded:  To be used with Dowload Report.  Name and extension of zip file to verify has been dowloaded.
        """

        if submenu == "View Tax Data Details":
            pass
        elif submenu == "View Tax Data Summary":
            pass
        elif submenu == "Print":
            pass
        else:
            assert False, "{} is not a valid submenu".format(submenu)

        actionCol = self.driver.find_element(By.XPATH, "//div[@class='page-menu u-inline-block u-float-right u-relative']")
        actionMenu = actionCol.find_element(By.XPATH, "//button[@class='btn btn--secondary menu btn--with-icon']")
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(actionMenu).perform()
        actionMenu.click()

        submenu = actionMenu.find_element(By.XPATH, "//div[contains(text(),'{}')]".format(submenu))
        actionChains.move_to_element(submenu).perform()
        submenu.click()

        if reportDownloaded != '':
            if os.path.exists("C:\\test\\_data\\_selenium_data"):
                print ('Download successful')
            else:
                assert False, ("Report did not download")

    def verify_zoom_dropdown_option(self):
        """
        This component will verify the zoom dropdown options available from minimum through maximum on view report page,
        and also verify default zoom option when report loaded.
        :param: None
        :return: None
        """
        expected_zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']

        try:
            zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
            zoom_dropdown_ele.click()
            select = Select(zoom_dropdown_ele)
        except (NoSuchElementException, TimeoutException):
            print(" the zoom dropdown element could not find")
        print("###selected zoom option:" + select.first_selected_option.text)

         #Verify default zoom option as 100%
        default_zoom_level = '100%'
        assert select.first_selected_option.text == default_zoom_level, "Error: Default Zoom option not setup as {}.".format(default_zoom_level)
        actual_zoom_dropdown_list = []
        for option in select.options:
            if 'Select' not in option.text:
                actual_zoom_dropdown_list.append(option.text)
            #print(option.text, option.get_attribute('value'))
        #verify 7 zoom level options
        assert expected_zoom_dropdown_list == actual_zoom_dropdown_list, "Error: Zoom dropdown list are not matching with expected dropdown list."

    def click_all_zoom_options(self):
        """
        This component will verify all zoom dropdown options one by one are selectable/ clickable on view report page,
        :param: None
        :return: None
        """
        expected_zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']

        try:
            zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
            zoom_dropdown_ele.click()
            select = Select(zoom_dropdown_ele)
        except (NoSuchElementException, TimeoutException):
            print(" the zoom dropdown element could not find")

        for zoom in range(len(expected_zoom_dropdown_list)):
            select.select_by_visible_text(expected_zoom_dropdown_list[zoom])
            time.sleep(1)
        print("###selected zoom option:" + select.first_selected_option.text)

    def click_random_zoom_option_and_verify(self):
        """
        This component will check randomly select any zoom option from zoom dropdown options and
        the percentage shown in the selector accordingly on view report page,
        :param: None
        :return: None
        """
        zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']
        try:
            zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
            zoom_dropdown_ele.click()
            select = Select(zoom_dropdown_ele)
        except(NoSuchElementException, TimeoutException):
            print(" the zoom dropdown element could not find")
        #randomly select Zoom
        randomly_selected_zoom_option = random.choice(zoom_dropdown_list)
        select.select_by_visible_text(randomly_selected_zoom_option)
        current_zoom_option = select.first_selected_option.text
        print("###selected zoom option:" + current_zoom_option)
        assert current_zoom_option == randomly_selected_zoom_option, "Error: Selected zoom option and current zoom option doesn't match."

    def verify_zoom_in_btn_progress_level_maximum_percentage(self):
        """
        This component will verify maximum percentage can progress by Zoom In Button click on view report page,
        :param: None
        :return: None
        """
        zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']
        try:
            zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
            #zoom_dropdown_ele.click()
            select = Select(zoom_dropdown_ele)
        except (NoSuchElementException, TimeoutException):
            print(" the zoom dropdown element could not find")

        for i in range(1,len(zoom_dropdown_list)+1):
            zoom_in_btn = self.driver.find_element(By.XPATH, "//button[@type='button']//span[text() = 'Zoom In']")
            zoom_in_btn.click()
            time.sleep(.5)
        current_zoom_option = select.first_selected_option.text
        expected_zoom = '200%'
        #verify max zoom value
        assert current_zoom_option == expected_zoom, "Error: max zoom {} did not match".format(expected_zoom)

    def verify_zoom_out_btn_progress_level_minimum_percentage(self):
        """
        This component will verify minimum percentage can decrease by Zoom Out Button click on view report page,
        :param: None
        :return: None
        """
        zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']
        try:
            zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
            #zoom_dropdown_ele.click()
            select = Select(zoom_dropdown_ele)
        except (NoSuchElementException, TimeoutException):
            print(" the zoom dropdown element could not find")

        for i in range(1,len(zoom_dropdown_list)+1):
            zoom_out_btn = self.driver.find_element(By.XPATH, "//button[@type='button']//span[text() = 'Zoom Out']")
            zoom_out_btn.click()
            time.sleep(.5)
        current_zoom_option = select.first_selected_option.text
        expected_zoom = '25%'
        #verify max zoom value
        assert current_zoom_option == expected_zoom, "Error: max zoom {} did not match".format(expected_zoom)

    def selecting_zoom_option(self, selectedZoom):
        """
        This component will select zoom option by using given param from zoom dropdown on view report page,
        :param: selectedZoom: type 'str': parameter will take only zoom options which is available through zoom dropdown.
        :return: None
        """
        zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']
        if selectedZoom in zoom_dropdown_list:
            try:
                zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
                select = Select(zoom_dropdown_ele)
                select.select_by_visible_text(selectedZoom)
            except (NoSuchElementException, TimeoutException):
                print(" the zoom dropdown element could not find")
        else:
            raise TypeError("Enter invalid zoom option.")

    def verify_current_zoom_option(self, expectedZoom):
        """
        This component will verify, what zoom option is selected now and checking expected zoom option as param is matching or not on view report page,
        :param: expectedZoom: type 'str': parameter will take only zoom options which is available through zoom dropdown.
        :return: None
        """
        zoom_dropdown_list = ['25%','50%','75%','100%','125%','150%','200%']
        current_zoom_option = None
        if expectedZoom in zoom_dropdown_list:
            try:
                zoom_dropdown_ele = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(ReturnPreview.ZOOM_DROPDOWN))
                self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", zoom_dropdown_ele, "background:yellow; color: Red; border: 3px dotted solid yellow;")
                select = Select(zoom_dropdown_ele)
                current_zoom_option = select.first_selected_option.text
            except (NoSuchElementException, TimeoutException):
                print(" the zoom dropdown element could not find")
        assert current_zoom_option == expectedZoom, "Error: zoom option not matching with Expected: '{}' to Actual:'{}'.".format(expectedZoom, current_zoom_option)

    def verify_line_item_action_menu(self, lineCode, fieldType):
        """Component will locate the field in the return preview based on the line code provided and verify both the count
        and labels of each menu item in the Action Menu based on field type (numeric or nonnumeric).
        Note that the component does not validate if menu is enabled, only it's presence and label.

        :param lineCode:  The line code of the field to locate in the return preview (Ex: LC_RET_REG_NUM)
        :param fieldType:  Enter 'numeric' or 'nonnumeric'"""

        numeric = ['Override Field', 'View Field Attributes', 'View Tax Data Details', 'View Tax Data Summary']
        nonnumeric = ['Override Field']

        # Find line in preview, click to make action menu button visible
        actionChains = ActionChains(self.driver)
        xpathLine = self._format_tuple(Endpoints.LINE, lineCode)
        line = self.driver.find_element(*xpathLine)
        actionChains.move_to_element(line)
        line.click()

        # Click Action Menu button
        xpathMenu = self._format_tuple(Endpoints.LINE_ACTION_MENU, lineCode)
        actionMenu = line.find_element(*xpathMenu)
        actionChains.move_to_element(actionMenu).perform()
        actionMenu.click()

        # Get menu count
        xpathContainer = self._format_tuple(Endpoints.LINE_ACTION_CONTAINER, lineCode)
        count = len(self.driver.find_elements(*xpathContainer))

        # Verify menu count and labels based on field type
        if fieldType.lower() == 'numeric':
            if count != len(numeric):
                assert False, "The number of Action Menu items present ({}) does not equal the expected count ({}) for numeric fields".format(count, str(len(numeric)))
            for item in numeric:
                xpathItem = self._format_tuple(Endpoints.LINE_ACTION_ITEM, item)
                menuItem = self.driver.find_element(*xpathItem)
                self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", menuItem, "background:yellow; color: Red; border: 3px dotted solid yellow;")
        elif fieldType.lower() == 'nonnumeric':
            if count != len(nonnumeric):
                assert False, "The number of Action Menu items present ({}) does not equal the expected count ({}) for non-numeric fields".format(count, str(len(nonnumeric)))
            for item in nonnumeric:
                xpathItem = self._format_tuple(Endpoints.LINE_ACTION_ITEM, item)
                menuItem = self.driver.find_element(*xpathItem)
                self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", menuItem, "background:yellow; color: Red; border: 3px dotted solid yellow;")
        else:
            assert False, "'{}' is not a valid value for fieldType.  Must enter 'numeric' or 'nonnumeric'".format(fieldType)
