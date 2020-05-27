"""
This module contains components for the GC Tax Data Details Page
"""
from selenium import webdriver
from lib.ui.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import calendar
import glob
import os


class Endpoints(object):
    FORM_LABEL_MULTI = (By.XPATH, "//p[contains(text(),'{}')]")
    CHANGES_MODAL = (By.XPATH, "//div[@class='modaal-content-row']")
    MODAL = (By.XPATH, ".//div[@class='modaal-container']")
    GRID = (By.XPATH, ".//div[@role='grid']")
    GRID_HEADERS = (By.XPATH, "//div[@class='ag-header-cell ag-header-cell-sortable']")
    GRID_HEADER_TEXT = (By.XPATH, ".//span[@role='columnheader']")
    GRID_HEADER_SORT = (By.CLASS_NAME, "ag-header-cell-sortable")  # used to sort by col header asc/desc
    GRID_HEADER_MENU_BUTTON = (By.XPATH, "//span[@ref='eMenu']")
    GRID_FILTER_MENU = (By.XPATH, "//div[@class='ag-menu ag-ltr']")
    GRID_FILTER_MENU_TAB = (By.XPATH, "//div[@ref='tabHeader']")
    GRID_ROW_CONTAINER = (By.CLASS_NAME, 'ag-center-cols-container')
    ALL_GRID_ROWS = (By.XPATH, ".//div[@role='row']")
    GRID_ROW = (By.XPATH, "//div[@ref='eCenterContainer']/div[@row-id='{}']")
    HORIZONTAL_SCROLL = (By.XPATH, "//div[@ref='eBodyHorizontalScrollViewport']")
    CELL_TOOLTIP = (By.XPATH, "//div[@data-automation-id='tooltip']")
    COMPANY_SELECT = (By.CSS_SELECTOR, "div#tax-data-filters-country-multiselect div.multiSelect__input")
    SELECT_BOX = (By.CSS_SELECTOR, "div#{} input[id^='react-select']")


class TaxDataDetails(BasePage):

    # Initializer
    def __init__(self, driver):
        BasePage.__init__(self, driver)

    def taxDataDetails_select_filter(self, filterLabel, valueToSelect, beginDate=''):
        """
        Clicks the specified filter element and adds the given filters.
        Use multiple times to enter multiple filters.

        :param filterLabel:  Filter label as seen in the UI (Ex: Company *)
        :param valueToSelect: Value to select as seen in the UI (Ex: AUS - Australia, Select All)
        :param beginDate:  Optional parameter.  Use when filterLabel is set to Allocation Date.  Set to True for beginning, False for ending.
        """
        try:
            company_select = WebDriverWait(self.driver, 120).until(EC.element_to_be_clickable(Endpoints.COMPANY_SELECT))
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", company_select, "backgroundColor: transparent; color: Green;")
            #self.driver.execute_script("arguments[0].click();", company_select)
        except (NoSuchElementException, TimeoutException):
            assert False, "Error: TaxDataDetails page WebElement is not clickable."

        formLabel = self.driver.find_element(By.XPATH, "//label[contains(text(), '{}')]".format(filterLabel))
        if "Date" in filterLabel:
            if beginDate == "true":
                dateBox = self.driver.find_element(By.XPATH,
                                                   "//div[@class='row']//div[1]//div[1]//div[1]//div[1]//input[1]")
                dateBox.click()
                input = self.driver.find_element(By.XPATH,
                                                 "//div[@class='row']//div[1]//div[1]//div[1]//div[1]//input[1]")
                input.click()
            elif beginDate == "false":
                dateBox = self.driver.find_element(By.XPATH,
                                                   "//div[@class='col-sm-4']//div[2]//div[1]//div[1]//div[1]//input[1]")
                dateBox.click()
            else:
                assert False, '{} is not a valid boolean for beginDate. Must be set to True or False.'
            self._date_picker_calender_widget(valueToSelect)
        else:
            id = formLabel.get_attribute('for')
            #below code is original
            '''
            select_box = self.driver.find_element(By.XPATH,
                                                  "//div[@id='{}']//div[contains(@class,'css-1hwfws3')]".format(id))
            select_box.click()
            input = select_box.find_element(By.TAG_NAME, 'input')
            input.send_keys(valueToSelect)
            input.send_keys(Keys.ENTER)
            '''
            #below code is new to better handle the inputbox
            try:
                select_field = self._format_tuple(Endpoints.SELECT_BOX, id)
                select_box = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located(select_field))
                time.sleep(1)
                select_box.send_keys(valueToSelect)
                time.sleep(1)
                select_box.send_keys(Keys.ENTER)
            except (ElementNotInteractableException, ElementClickInterceptedException ):
                try:
                    time.sleep(1)
                    print("Error: exception throws and try 2nd time")
                    select_field = self._format_tuple(Endpoints.SELECT_BOX, id)
                    select_box = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable(select_field))
                    self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", select_box, "background:yellow; color: Red; border: 3px dotted solid yellow;")
                    #select_box.send_keys(valueToSelect)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].value='{}';".format(valueToSelect), select_box)
                    time.sleep(1)
                    select_box.send_keys(Keys.ENTER)
                except :
                    assert False, "Select_box throwing exception in 2nd time. and stop executing the test."


    def taxDataDetails_scroll_right_of_grid(self, columnName):
        """
        Scrolls the grid horizonally from left to right until it finds the specified column name.

        NOTE: Use taxDataDetails_scroll_down_of_grid first

        : param columnName : Name of column to find as shown in UI
        : return : None
        """
        self._scroll_to_grid()
        actionChains = ActionChains(self.driver)
        # scrollBar = self.driver.find_element(*Endpoints.HORIZONTAL_SCROLL)
        # scrollBar.click()

        # Force the bar to the left at beginning
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_elements(*Endpoints.GRID)[1]
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADERS))
        headers = grid.find_elements(*Endpoints.GRID_HEADERS)
        headerList = []
        for header in headers:
            WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
            headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
            headerList.append(headerText.lower())

        # print(headerList)
        if columnName.lower() in headerList:
            getCol = grid.find_element_by_xpath(
                "//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
            self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
            return
        # Start scrolling right until header if found or headers do not change (end of scroll)
        newHeaders = []
        while newHeaders != headerList:
            print('OLD', headerList)
            print('NEW', newHeaders)
            headerList = newHeaders
            # Scroll right 15 times.
            print('Scrolling Right...')
            for e in range(2):
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
            time.sleep(2)
            newHeaders = []
            headers = grid.find_elements(*Endpoints.GRID_HEADERS)
            # Get all headers
            for header in headers:
                WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
                headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
                newHeaders.append(headerText.lower())
            print(newHeaders)
            if columnName.lower() in newHeaders:
                getCol = grid.find_element_by_xpath(
                    "//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
                self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
                return

        assert False, 'No column found with the name ' + columnName

    def taxDataDetails_scroll_down_of_grid(self, rowNum):
        """
        Finds the specified row number and scrolls down the grid if needed. Clicks on the row when found.

        : param rowNum : Row number to find, starting at 0
        : return : None
        """
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self._scroll_to_grid()
        actionChains = ActionChains(self.driver)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_elements(*Endpoints.GRID)[1]
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_ROW_CONTAINER))
        rowContainer = grid.find_element(*Endpoints.GRID_ROW_CONTAINER)
        rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
        rowList = []
        for row in rows:
            rowValue = row.get_attribute("row-index")
            # print(rowValue)
            rowList.append(str(rowValue))

        # print(rowList)
        if rowNum in rowList:
            getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowNum + "']")
            self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
            actionChains.move_to_element(getRow).perform()
            actionChains.click(getRow).perform()
            time.sleep(5)
            return
        # Scroll to the last row displayed on grid
        # print(rowList[-1])
        getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowList[-1] + "']")
        self.driver.execute_script('arguments[0].scrollIntoView();', getRow)

        # Start scrolling right until header if found or headers do not change (end of scroll)
        newRows = []
        while newRows != rowList:
            # print('OLD', rowList)
            # print('NEW', newRows)
            rowList = newRows
            # Scroll down 15 times.
            print('Scrolling Down...')
            for e in range(4):
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
            time.sleep(2)
            newRows = []
            rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
            # Get all headers
            for row in rows:
                rowValue = row.get_attribute("row-index")
                # print(rowValue)
                newRows.append(str(rowValue))
            # print(newRows)
            if rowNum in newRows:
                getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowNum + "']")
                self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
                actionChains.move_to_element(getRow).perform()
                actionChains.click(getRow).perform()
                time.sleep(5)
                return

        assert False, 'No row found with the number {}'.format(rowNum)

    def taxDataDetails_inv_list_toggle(self):

        """Will toggle the Invoice List section of the page by clicking the '+' or '-' button.
        If list is collapsed, then component will expand.  If expanded, it will collapse the list."""

        invList = self.driver.find_element(By.XPATH,"//span[contains(text(),'Tax Data Detail Records')]/ancestor::li//div[contains(@class,'accordion__panel-title')]")
        invList.click()

    def taxDataDetails_edit_value_within_grid(self, cellValue, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.double_click(rowCell).perform()
        cellBox = rowCell.find_element(By.TAG_NAME, 'input')
        cellBox.send_keys(cellValue)
        cellBox.send_keys(Keys.ENTER)

    def taxDataDetails_click__edited_value_within_grid(self, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.double_click(rowCell).perform()
        # cellBox = rowCell.find_element(By.TAG_NAME, 'input')
        # cellBox.send_keys(cellValue)
        # cellBox.send_keys(Keys.ENTER)


    def taxDataDetails_verify_value_within_grid(self, expectedValue, rowNum, columnName):
        """
        IN PROGRESS - DO NOT USE
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        rowCellValue = rowCell.find_element(By.XPATH, ".//div[contains(@class, 'changed-field-renderer')]").text
        if rowCellValue == expectedValue:
            pass
        else:
            assert False, "Actual cell value is " + rowCellValue + " when the expected value is {}.".format(
                expectedValue)

    def taxDataDetails_verify_colored_triangle(self, expectedColorTriangle, rowNum, columnName):
        """
        Verify expected colored triangle within specified editable grid.

        : param expectedColorTriangle : Either 'yellow' or 'blue'
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        rowCellSection = rowCell.find_element(By.XPATH, ".//div[contains(@class, 'changed-field-renderer')]")
        cellAttribute = rowCellSection.get_attribute('class')
        # print(cellAttribute)

        if "unsaved-change" in cellAttribute:
            if expectedColorTriangle.lower() == 'blue':
                pass
            elif expectedColorTriangle.lower() == 'yellow':
                assert False, "Expected colored triangle was yellow but actual colored triangle for the cell was blue."
            else:
                assert False, "Expected colored triangle input was not either yellow or blue."
        else:
            if expectedColorTriangle.lower() == 'yellow':
                pass
            elif expectedColorTriangle.lower() == 'blue':
                assert False, "Expected colored triangle was blue but actual colored triangle for the cell was yellow."

            else:
                assert False, "Expected colored triangle input was not either yellow or blue."

    def taxDataDetails_close_save_modal(self):
        """
        Close the modal after successful save of changes within the Tax Data Details grid.

        : return : None
        """
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.MODAL))
        modal = self.driver.find_element(*Endpoints.MODAL)
        modal.find_element(By.ID, 'modaal-close').click()

    def taxDataDetails_verify_tooltip(self, rowNum, columnName, isExpected, expectedValue=''):
        """
        Verify the value within the tooltip when hovering over an specific grid cell in Tax Data Details

        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column
        : param isExpected : 'true' of 'false' if tooltip is expected when hovering over the cell
        : param expectedValue : Expected value within the tooltip if isExpected param is set to 'true'; Defaults to empty
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        time.sleep(1)
        try:
            #WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.CELL_TOOLTIP))
            toolTip = self.driver.find_element(*Endpoints.CELL_TOOLTIP)
            toolValue = toolTip.find_element(By.TAG_NAME, 'span').text
            if isExpected == 'true':
                if expectedValue in toolValue:
                    pass
                else:
                    assert False, "Expected value of {} does not match with the actual value of {} within the edited tooltip".format(expectedValue, toolValue)
            else:
                if expectedValue in toolValue:
                    assert False, "Tooltip was expected not to appear but actual result shows that it did appear"
                else:
                    pass
        except NoSuchElementException:
            if isExpected == 'false':
                pass
            else:
                assert False, "Tooltip was expected to appear but actual result shows that it did not appear"

    ############################
    #   Verify Components    #
    ############################
    def context_tab_switching(self):
        """This method will click context tab  """
        time.sleep(5)
        context_tab = self.driver.find_element(By.XPATH, "//button[@id='tab-context']")
        context_tab.click()

    def selection_criteria_tab(self):
        """This method will click selection criteria tab """
        time.sleep(5)
        selection_criteria_tab = self.driver.find_element(By.XPATH, "//li[@id='selection']")
        selection_criteria_tab.click()


    def select_Multiselect_taxdata_page(self):
        # """ This method will click all the multiselect dropdown present in tax summarry based on automation-id"""
        # company dropdown
        time.sleep(90)
        select_box_9 = self.driver.find_element(By.XPATH, "(//div[@class=' css-osmud9-indicatorContainer'])[1]")
        select_box_9.click()
        time.sleep(15)
        select_box_10 = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        select_box_10.click()
        time.sleep(15)
        select_box_9 = self.driver.find_element(By.XPATH, "(//div[@class=' css-osmud9-indicatorContainer'])[2]")
        select_box_9.click()
        time.sleep(15)
        select_box_10 = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        select_box_10.click()
        time.sleep(15)
        start_date = self.driver.find_element(By.XPATH, "//div[@data-automation-id='calendar-dateRange-startRange']")
        start_date.click()
        time.sleep(15)
        input_date_first = self.driver.find_element(By.XPATH,
                                                    "//div[@class='react-datepicker__day react-datepicker__day--030']")
        input_date_first.click()
        time.sleep(15)
        apply_button = self.driver.find_element(By.XPATH, "//button[text()='Apply Filters']")
        apply_button.click()
        time.sleep(15)
        value = self.driver.find_element(By.XPATH, "//button[@id='tab-context']")
        #      Print(value)
        time.sleep(15)


    def select_Multiselect_taxdata_page(self) :
        #""" This method will click all the multiselect dropdown present in tax summarry based on automation-id"""
          #company dropdown
          time.sleep(90)
          select_box_9 =self.driver.find_element(By.XPATH,"(//div[@class=' css-osmud9-indicatorContainer'])[1]")
          select_box_9 .click()
          time.sleep(15)
          select_box_10  = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
          select_box_10.click()
          time.sleep(15)
          select_box_9 =self.driver.find_element(By.XPATH,"(//div[@class=' css-osmud9-indicatorContainer'])[2]")
          select_box_9 .click()
          time.sleep(15)
          select_box_10  = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
          select_box_10.click()
          time.sleep(15)
          start_date = self.driver.find_element(By.XPATH, "//div[@data-automation-id='calendar-dateRange-startRange']")
          start_date.click()
          time.sleep(15)
          input_date_first=self.driver.find_element(By.XPATH, "//div[@class='react-datepicker__day react-datepicker__day--030']")
          input_date_first.click()
          time.sleep(15)
          apply_button=self.driver.find_element(By.XPATH, "//button[text()='Apply Filters']")
          apply_button.click()
          time.sleep(15)
          value = self.driver.find_element(By.XPATH, "//button[@id='tab-context']")
    #      Print(value)
          time.sleep(15)

    def get_view_taxdatadetails_count_twenty(self,expectedcellvalue):

        """ This method is to get the count of the button"""
        time.sleep(5)
        viewtaxdatadetailsbuttoncount = self.driver.find_element(By.XPATH,
                                                                 "//button[@title='VIEW TAX DATA DETAILS (20)']").text
        print("test=" + viewtaxdatadetailsbuttoncount)
        assert expectedcellvalue == viewtaxdatadetailsbuttoncount, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(
            e=expectedcellvalue, a=cell_val)

    def get_view_taxdatadetails_count_two(self, expectedcellvalue):
        """ This method is to get the count of the button"""
        time.sleep(5)
        viewtaxdatadetailsbuttoncount = self.driver.find_element(By.XPATH,
                                                                 "//button[@title='VIEW TAX DATA DETAILS (2)']").text
        print("test=" + viewtaxdatadetailsbuttoncount)
        assert expectedcellvalue == viewtaxdatadetailsbuttoncount, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(
            e=expectedcellvalue, a=cell_val)

    def get_badge_value(self, expectedcellvalue):
        """This method will extract bage value as per the seingle selection made  """
        time.sleep(4)
        cell_val = self.driver.find_element(By.XPATH, "//button[text()='Context']/span").text
        assert expectedcellvalue == cell_val, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(
            e=expectedcellvalue, a=cell_val)

    def context_tab_cell_value(self, expectedcellvalue):
        """ This method will get the text value from context tab cell"""
        time.sleep(20)
        # cell_val = self.driver.find_element(By.XPATH, "//div[@class ='ag-cell ag-cell-not-inline-editing ag-cell-with-height ag-cell-value']").text
        cell_val = self.driver.find_element(By.XPATH,
                                            "//div[contains(text(),'Tax Data Details for Vertex Test Company')]").text
        # cell_val.get_attribute.text
        print("test=" + cell_val)
        assert expectedcellvalue == cell_val, "Expected and Actual header do not match. Expected: {e} Actual: {a}".format(
            e=expectedcellvalue, a=cell_val)

        assert expectedcellvalue == cell_val,"Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedcellvalue, a=cell_val)

    def context_tab_cell_value_top_20(self,expectedcellvalue,expectedcellvalueone):
     """ This method will get the text value from context tab cell"""
     time.sleep(20)
     #cell_val = self.driver.find_element(By.XPATH, "//div[@class ='ag-cell ag-cell-not-inline-editing ag-cell-with-height ag-cell-value']").text
     cell_val = self.driver.find_element(By.XPATH, "//div[contains(text(),'Tax Data Details for Vertex Test Company')]").text
    # cell_val.get_attribute.text
     print("test="+ cell_val)
     assert expectedcellvalue == cell_val,"Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedcellvalue, a=cell_val)
     cell_val=self.driver.find_element(By.XPATH, "//*[@id='context']/div/div/div/div/div/div/div[2]/div[1]/div[3]/div[4]/div[2]/div/div").text
     assert expectedcellvalueone == cell_val,"Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedcellvalue, a=cell_val)

    def context_tab_cell_value(self,expectedcellvalue):
     """ This method will get the text value from context tab cell"""
     time.sleep(20)
     #cell_val = self.driver.find_element(By.XPATH, "//div[@class ='ag-cell ag-cell-not-inline-editing ag-cell-with-height ag-cell-value']").text
     cell_val = self.driver.find_element(By.XPATH, "//div[contains(text(),'Tax Data Details for Vertex Test Company')]").text
    # cell_val.get_attribute.text
     print("test="+ cell_val)
     assert expectedcellvalue == cell_val,"Expected and Actual header do not match. Expected: {e} Actual: {a}".format(e=expectedcellvalue, a=cell_val)


    def verify_changes_in_grid_modal(self, savedFields, savedRecords, failedFields, failedRecords):
        """
        Verifies the expected saved changes and failed changes on the modal of Tax Data Details grid.

        : param savedFields : Number of expected saved fields (cells)
        : param savedRecords : Number of expected saved records (rows)
        : param failedFields : Number of expected failed fields (cells)
        : param failedRecords : Number of expected failed records (rows)
        : return : None
        """
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.CHANGES_MODAL))
        recordModal = self.driver.find_element(By.XPATH, "//div[@class='modaal-content-row']")
        recordModalStr = recordModal.text.split(' ')
        # print(recordModalStr[0], recordModalStr[3], recordModalStr[8], recordModalStr[11])
        if savedFields == recordModalStr[0] and savedRecords == recordModalStr[3]:
            pass
        else:
            # either saved fields or records are not matching with UI message
            if savedFields == recordModalStr[0]:
                assert False, "Expected saved records does not match with actual saved records: Actual - {}, Expected - {}".format(
                    recordModalStr[3], savedRecords)
            else:
                assert False, "Expected saved fields does not match with actual saved fields: Actual - {}, Expected - {}".format(
                    recordModalStr[0], savedFields)
        if failedFields == recordModalStr[8] and failedRecords == recordModalStr[11]:
            pass
        else:
            if failedFields == recordModalStr[8]:
                assert False, "Expected failed records does not match with actual failed records: Actual - {}, Expected - {}".format(
                    recordModalStr[8], failedRecords)
            else:
                assert False, "Expected failed fields does not match with actual failed fields: Actual - {}, Expected - {}".format(
                    recordModalStr[11], failedFields)

    ############################
    #   Internal Components    #
    ############################

    def _date_picker_calender_widget(self, date):

        """Internal component to select date (DD MMM YYYY) in calendar widget"""

        # Date to select as time tuple
        selectDate = time.strptime(date, "%d %b %Y")

        # Current date as time tuple
        currentDate = time.localtime()

        # Find dif in months between current month/year and desired month year
        yearDif = selectDate.tm_year - currentDate.tm_year
        monthDif = selectDate.tm_mon - currentDate.tm_mon
        totalClicks = yearDif * 12 + monthDif

        # Click previous or next months arrows
        if totalClicks == 0:
            pass
        elif totalClicks < 0:
            prevMonth = self.driver.find_element(By.XPATH,
                                                 ".//button[@class='react-datepicker__navigation react-datepicker__navigation--previous']")
            count = 0
            while count < abs(totalClicks):
                prevMonth.click()
                time.sleep(2)
                count = count + 1
        elif totalClicks > 0:
            nextMonth = self.driver.find_element(By.XPATH,
                                                 "//button[@class='react-datepicker__navigation react-datepicker__navigation--next']")
            count = 0
            while count < abs(totalClicks):
                nextMonth.click()
                time.sleep(2)
                count = count + 1

        # select day
        dayContainer = self.driver.find_element(By.XPATH, ".//div[@role='listbox']")
        # day = dayContainer.find_element(By.XPATH, "//div[contains(text(), '{}')]".format(str(selectDate.tm_mday)))
        # day.click()
        rows = dayContainer.find_elements_by_class_name('react-datepicker__week')
        foundDay = []
        for row in rows:
            days = row.find_elements_by_xpath(".//div[@role='option']")
            for day in days:
                # finds any matching day number and place xpath into list
                if day.text == str(selectDate.tm_mday):
                    foundDay.append(day)

        # selects the last number in the list in case both numbers are showing up from previous month
        if len(foundDay) > 1 and selectDate.tm_mday > 10:
            self.driver.execute_script("arguments[0].click();", foundDay[-1])
        elif len(foundDay) == 0:
            assert False, "Unable to find day: {}".format(str(selectDate.tm_mday))
        else:
            self.driver.execute_script("arguments[0].click();", foundDay[0])

    def _scroll_to_grid(self):
        """ internal component that scrolls to the grid for visibility """

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.HORIZONTAL_SCROLL))
        scrollBar = self.driver.find_elements(*Endpoints.HORIZONTAL_SCROLL)[0]
        self.driver.execute_script("arguments[0].scrollIntoView()", scrollBar)

    def _retrieve_cell_from_grid(self, rowNum, columnName):
        """ internal component that retrieve specified cell based on row index and column name """

        # gets the correct grid from accordion
        grid = self.driver.find_elements(*Endpoints.GRID)[0]
        # finds the row index
        xpath = self._format_tuple(Endpoints.GRID_ROW, int(rowNum))
        row = grid.find_element(*xpath)
        print(row.text)
        # finds the column name
        rowCell = row.find_element(By.XPATH, ".//div[@col-id='" + columnName + "']")
        print(rowCell.text)
        return rowCell

    def _validate_column_value(self, expectedColumnValues, actualColumnValues):
        columnValueList = expectedColumnValues.split("|")
        print(columnValueList)
        for actualColumnValue in actualColumnValues:
            exceptionMessage = "ActualValue {0} ".format(actualColumnValue)
            assert actualColumnValue in columnValueList, exceptionMessage

    def _validate_column_number_value(self, expectedColumnValues, actualColumnValues):
        columnValueList = expectedColumnValues.split("|")
        print(columnValueList)
        for actualColumnValue in actualColumnValues:
            exceptionMessage = "ActualValue {0} ".format(actualColumnValue)
            assert str(actualColumnValue) in columnValueList, exceptionMessage

    def _validate_date_column_values(self, startDate, endDate, actualColumnValues):
        expectedStartDate = time.strptime(startDate, "%Y-%m-%d")
        expectedEndDate = time.strptime(endDate, "%Y-%m-%d")
        for actualColumnValue in actualColumnValues:
            actualDate = time.strptime(actualColumnValue, "%Y-%m-%d")
            assert expectedStartDate <= actualDate <= expectedEndDate

    def _scroll_left(self):
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.HORIZONTAL_SCROLL))
        scrollBar = self.driver.find_elements(*Endpoints.HORIZONTAL_SCROLL)[0]
        self.driver.execute_script("arguments[0].scrollLeft += 250", scrollBar)
        time.sleep(30)

    def _export_as_csv(self):
        csv = self.driver.find_element(By.XPATH, "//button[@data-automation-id = 'button-commonGrid-exportAsCsv'][not(@disabled)]")
        csv.click()
        time.sleep(10)

       #Company Filter
    def company_selection_tax_details(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(20)
        Company_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-company-multiselect']//div//div)[1]")
        Company_placeholder.click()
        time.sleep(5)
        Company_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-company-multiselect']//div//div)[1]//following::input[@id='react-select-2-input']")
        Company_value.send_keys(value)
        Comapany_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Comapany_container.click()

    def company_selection(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(20)
        Company_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-company-multiselect']//div//div)[1]")
        Company_placeholder.click()
        time.sleep(5)
        Company_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-company-multiselect']//div//div)[1]//following::input[@id='react-select-2-input']")
        Company_value.send_keys(value)
        Comapany_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Comapany_container.click()

        #Country Filter
    def country_selection_tax_detail(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        Country_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]")
        Country_placeholder.click()
        time.sleep(5)
        Country_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]//following::input[@id='react-select-3-input']")
        Country_value.send_keys(value)
        Country_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Country_container.click()

    def country_selection(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        Country_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]")
        Country_placeholder.click()
        time.sleep(5)
        Country_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]//following::input[@id='react-select-3-input']")
        Country_value.send_keys(value)
        Country_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Country_container.click()
    #taxcode Filter

    def launch_site(self):
        time.sleep(15)
        Country_placeholder=self.driver.find_element(By.XPATH,"//a[contains(text(),'Launch Site')]")
        Country_placeholder.click()

    def country_selection(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        Country_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]")
        Country_placeholder.click()
        time.sleep(5)
        Country_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-country-multiselect']//div//div)[1]//following::input[@id='react-select-3-input']")
        Country_value.send_keys(value)
        Country_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        Country_container.click()
    #taxcode Filter
    def taxcode_selection(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        taxcode_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-tax-code-multiselect']//div//div)[1]")
        taxcode_placeholder.click()
        time.sleep(5)
        taxcode_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-tax-code-multiselect']//div//div)[1]//following::input[@id='react-select-4-input']")
        taxcode_value.send_keys(value)
        taxcode_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        taxcode_container.click()
    #Filing category Filter
    def taxcode_selection_tax_details(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        taxcode_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-tax-code-multiselect']//div//div)[1]")
        taxcode_placeholder.click()
        time.sleep(5)
        taxcode_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-tax-code-multiselect']//div//div)[1]//following::input[@id='react-select-4-input']")
        taxcode_value.send_keys(value)
        taxcode_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        taxcode_container.click()
    def filling_category_selection(self,value):
        """This method will basically take user input and select the multiselect dropdown """
        time.sleep(15)
        fillingcategory_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-category-multiselect']//div//div)[1]")
        fillingcategory_placeholder.click()
        time.sleep(5)
        fillingcategory_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-category-multiselect']//div//div)[1]//following::input[@id='react-select-5-input']")
        fillingcategory_value.send_keys(value)
        fillingcategory_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        fillingcategory_container.click()

    def filling_category_selection_tax_detail(self,value):
        """This method will basically take user input and select the multiselect dropdown """
        time.sleep(15)
        fillingcategory_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-category-multiselect']//div//div)[1]")
        fillingcategory_placeholder.click()
        time.sleep(5)
        fillingcategory_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-category-multiselect']//div//div)[1]//following::input[@id='react-select-5-input']")
        fillingcategory_value.send_keys(value)
        fillingcategory_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        fillingcategory_container.click()
    #Filling currency Filter
    def filling_currency_selection(self,value):
        """ This method will basically take user input and select the multiselect dropdown"""
        time.sleep(15)
        fillingcurrency_placeholder=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-currency-multiselect']//div//div)[1]")
        fillingcurrency_placeholder.click()
        time.sleep(5)
        fillingcurrency_value=self.driver.find_element(By.XPATH,"(//div[@id='tax-data-filters-filing-currency-multiselect']//div//div)[1]//following::input[@id='react-select-6-input']")
        fillingcurrency_value.send_keys(value)
        fillingcurrency_container = self.driver.find_element(By.XPATH, "//div[@class=' css-p4vj6b-menu']")
        fillingcurrency_container.click()

    def daterange_filter(self):
        """ """
        #self.((JavascriptExecutor)driver).executeScript ("document.getElementById('fromDate').removeAttribute('readonly',0);");
        time.sleep(5)
        from_date_placeholder=self.driver.find_element(By.XPATH,"(//div[@class='col-sm-6'])[1]")
        from_date_placeholder.Click()
        time.sleep(5)
        #dummy_date=self.driver.find_element(By.XPATH,"//div[@class='react-datepicker__day react-datepicker__day--001 react-datepicker__day--selected react-datepicker__day--weekend']")
        #dummy_date.click()
        for i in range(4):
            #loop to click four times previous month button
            previous_month_button=self.driver.find_element(By.XPATH,("//button[@class='react-datepicker__navigation react-datepicker__navigation--previous']"))
            previous_month_button.click()
            time.sleep(5)
        date_vaue_startrange=self.driver.find_element(By.XPATH,("//div[@class='react-datepicker__day react-datepicker__day--001 react-datepicker__day--weekend']"))
        date_vaue_startrange.click()
        time.sleep(5)
        to_date_placeholder=self.driver.find_element(By.XPATH,("//div[@data-automation-id='calendar-dateRange-endRange']//div//input"))
        to_date_placeholder.click()
        time.sleep(5)

    def importpage_scroll_down_of_grid(self, rowNum):
        """
        Finds the specified row number and scrolls down the grid if needed. Clicks on the row when found.

        : param rowNum : Row number to find, starting at 0
        : return : None
        """
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        self._scroll_to_grid()
        actionChains = ActionChains(self.driver)

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_elements(*Endpoints.GRID)[0]
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_ROW_CONTAINER))
        rowContainer = grid.find_element(*Endpoints.GRID_ROW_CONTAINER)
        rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
        rowList = []
        for row in rows:
            rowValue = row.get_attribute("row-index")
            # print(rowValue)
            rowList.append(str(rowValue))

        # print(rowList)
        if rowNum in rowList:
            getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowNum + "']")
            self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
            actionChains.move_to_element(getRow).perform()
            actionChains.click(getRow).perform()
            time.sleep(5)
            return
        # Scroll to the last row displayed on grid
        # print(rowList[-1])
        getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowList[-1] + "']")
        self.driver.execute_script('arguments[0].scrollIntoView();', getRow)

        # Start scrolling right until header if found or headers do not change (end of scroll)
        newRows = []
        while newRows != rowList:
            # print('OLD', rowList)
            # print('NEW', newRows)
            rowList = newRows
            # Scroll down 15 times.
            print('Scrolling Down...')
            for e in range(4):
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
                actionChains.send_keys(Keys.DOWN).perform()
            time.sleep(2)
            newRows = []
            rows = rowContainer.find_elements(*Endpoints.ALL_GRID_ROWS)
            # Get all headers
            for row in rows:
                rowValue = row.get_attribute("row-index")
                # print(rowValue)
                newRows.append(str(rowValue))
            # print(newRows)
            if rowNum in newRows:
                getRow = rowContainer.find_element_by_xpath(".//div[@row-index='" + rowNum + "']")
                self.driver.execute_script('arguments[0].scrollIntoView();', getRow)
                actionChains.move_to_element(getRow).perform()
                actionChains.click(getRow).perform()
                time.sleep(5)
                return

        assert False, 'No row found with the number {}'.format(rowNum)

    def importpage_scroll_right_of_grid(self, columnName):
        """
        Scrolls the grid horizonally from left to right until it finds the specified column name.

        NOTE: Use taxDataDetails_scroll_down_of_grid first

        : param columnName : Name of column to find as shown in UI
        : return : None
        """
        self._scroll_to_grid()
        actionChains = ActionChains(self.driver)
        # scrollBar = self.driver.find_element(*Endpoints.HORIZONTAL_SCROLL)
        # scrollBar.click()

        # Force the bar to the left at beginning
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()
        # actionChains.send_keys(Keys.LEFT).perform()

        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID))
        grid = self.driver.find_elements(*Endpoints.GRID)[0]
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADERS))
        headers = grid.find_elements(*Endpoints.GRID_HEADERS)
        headerList = []
        for header in headers:
            WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
            headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
            headerList.append(headerText.lower())

        # print(headerList)
        if columnName.lower() in headerList:
            getCol = grid.find_element_by_xpath(
                "//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
            self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
            return
        # Start scrolling right until header if found or headers do not change (end of scroll)
        newHeaders = []
        while newHeaders != headerList:
            print('OLD', headerList)
            print('NEW', newHeaders)
            headerList = newHeaders
            # Scroll right 15 times.
            print('Scrolling Right...')
            for e in range(2):
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
                actionChains.send_keys(Keys.RIGHT).perform()
            time.sleep(2)
            newHeaders = []
            headers = grid.find_elements(*Endpoints.GRID_HEADERS)
            # Get all headers
            for header in headers:
                WebDriverWait(header, 30).until(EC.presence_of_element_located(Endpoints.GRID_HEADER_TEXT))
                headerText = header.find_element(*Endpoints.GRID_HEADER_TEXT).text
                newHeaders.append(headerText.lower())
            print(newHeaders)
            if columnName.lower() in newHeaders:
                getCol = grid.find_element_by_xpath(
                    "//span[@role='columnheader' and contains(text(), '" + columnName + "')]")
                self.driver.execute_script('arguments[0].scrollIntoView();', getCol)
                return

        assert False, 'No column found with the name ' + columnName

    def import_edit_value_within_grid(self, cellValue, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.click(rowCell).perform()

    def taxdetail_click_value_within_grid(self, cellValue, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.click(rowCell).perform()

    def taxdetail_double_click_value_within_grid(self, rowNum, columnName):
        """
        Edits specified value within the grid based on the row index and column name.

        : param cellValue : New value of the specified cell
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        # moves towards the specified cell within grid
        actionChains = ActionChains(self.driver)
        actionChains.move_to_element(rowCell).perform()
        # double-clicks within the cell
        actionChains.double_click(rowCell).perform()

    def taxDataDetails_verify_existence_of_triangle(self, rowNum, columnName):
        """
        Verify expected colored triangle within specified editable grid.

        : param expectedColorTriangle : Either 'yellow' or 'blue'
        : param rowNum : Row index within the grid, starting at 0
        : param columnName : Name of the column as shown in the UI
        : return : None
        """
        rowCell = self._retrieve_cell_from_grid(rowNum, columnName)
        rowCellSection = rowCell.find_elements(By.XPATH, ".//div[@class = 'changed-field-renderer']")
        print(len(rowCellSection))
        if len(rowCellSection) == 1:
            pass
        else:
            assert False, "Expected triangle should not be present but triangle is listed"
