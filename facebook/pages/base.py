import logging
from random import randint
from time import sleep

import pyperclip as pyperclip
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from splinter.driver import ElementAPI
from splinter.driver.webdriver import BaseWebDriver
from splinter.element_list import ElementList

from common import SELECTORS, Selector

HIGHLIGHT_STYLE = "background: yellow; border: 2px solid red;"
# Max number of loops for clicking on expanders
MAX_LOOPING = 4


class BasePage:
    """Base class for pages with some helper functions"""

    def __init__(self, browser, logger: logging.Logger = logging.getLogger("fb_Page")):
        self.browser: BaseWebDriver = browser
        self.logger = logger

    @property
    def profile_button(self):
        return self.find(SELECTORS.profileBtn)

    @property
    def firstname(self):
        """
        Get first name of the user from left drawer panel
        :return:
        """
        # if self.find(SELECTORS.profileBtnDiv).is_displayed():
        #     self.find(SELECTORS.profileBtnDiv).click()
        #     self.is_present(SELECTORS.fName, 5)
        #     sleep(2)
        #     fName = SELECTORS.fName
        #     ActionChains(self.browser.driver).send_keys(Keys.ESCAPE).perform()
        #
        #     return fName

        return self.find(SELECTORS.fName)

    @property
    def firstname_old(self):
        """
        Get first name of the user from  left drawer panel for old ui
        :return:
        """
        return self.find(SELECTORS.fName_old)

    def scroll_randomly(self):
        """
        Randomly scroll to mimic human behaviour
        """
        for i in range(randint(4, 8)):
            self.browser.execute_script(f'window.scrollBy(0,{randint(400, 1000)})', '')
            sleep(randint(2, 4))

    def scroll(self, count=6):
        for i in range(count):
            self.browser.execute_script(f'window.scrollBy(0, 400)', '')
            sleep(1)

    def scroll_top(self):
        # Scroll to the top of the page
        self.browser.find_by_xpath('//body').type(Keys.CONTROL + Keys.HOME)
        sleep(2)

    def find(self, selector: Selector, replace_target: str = None, replacement: str = None) -> ElementList:
        """
        Helper method to find elements by xpath with optional on the fly replacements
        :param replacement: actual value to be replaced with from the xpath
        :param replace_target: a dummy value in the Selector xpath to be replaced
        :param selector:
        :return: splinter webelement list
        """
        # Return first element list found by given xpaths
        for xpath in selector.xpaths:
            if replacement and replace_target:
                xpath = xpath.replace(replace_target, replacement)
            elements = self.browser.find_by_xpath(xpath)
            if elements:
                return elements

    def is_present(self, selector: Selector, duration: int) -> bool:
        """Helper method to wait for presence of an element upto duration seconds"""
        for xpath in selector.xpaths:
            elements = self.browser.is_element_present_by_xpath(xpath, duration)
            if elements:
                return True
        return False

    def is_not_present(self, selector: Selector, duration: int):
        """Helper method to wait for an element to be gone upto duration seconds"""
        for xpath in selector.xpaths:
            self.browser.is_element_not_present_by_xpath(xpath, duration)

    def is_clickable(self, selector: Selector, duration: int = 30):
        """Helper method to wait for an element to be clickable waiting upto duration seconds"""
        for xpath in selector.xpaths:
            WebDriverWait(self.browser.driver, duration).until(EC.element_to_be_clickable((By.XPATH, xpath)))

    def hover(self, element):
        """
        Hover over given element
        :param element: splinter web element
        :return:
        """
        ActionChains(self.browser.driver).move_to_element(
            self.find(SELECTORS.fbLogo)._element).move_to_element(
            element._element).perform()

    def send_key(self, key):
        ActionChains(self.browser.driver).send_keys(key).perform()

    def highlight(self, element: ElementAPI):
        """Highlight the given element"""
        self.browser.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                    element._element, HIGHLIGHT_STYLE)

    def click_all(self, selector: Selector):
        self.logger.info(f">> Check {selector.description}")
        # Try to check the pager count before comment processing and make sure it's zero in this loop
        last_count = 0
        looping = 0
        while True:
            try:
                element = self.find(selector)
                if not element:
                    break
                current_count = len(element)
                if looping >= MAX_LOOPING:
                    # Todo: raise some known error here for caller to catch
                    return False
                # If the expanders count is same then increment looper
                if current_count == last_count:
                    looping += 1
                else:
                    looping = 0
                last_count = current_count
                self.browser.execute_script("arguments[0].scrollIntoView(true);", element._element)
                # Scroll up a little in case of some headers in some websites
                self.browser.execute_script("window.scrollBy(0, -200);")
                self.hover(element)
                sleep(1)
                element.click()
                sleep(2)
            except StaleElementReferenceException:
                pass
            except TypeError:
                pass
            except Exception:
                # Only for spam
                self.logger.exception("Unable to click on the 3 dots...")
        # Go to top of the page once all the expanders are clicked
        self.scroll_top()
        return True

    def paste_text_from_cb(self):
        """
        Paste from clipboard into browser
        :return:
        """
        ActionChains(self.browser.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(self.browser.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        sleep(1)

    def copy_text_to_cb(self):
        """
        Copy to clipboard from browser
        :return:
        """
        ActionChains(self.browser.driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        sleep(1)
        ActionChains(self.browser.driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
        sleep(1)

    @staticmethod
    def cb_write(data):
        """
        Write data to clipboard
        :return:
        """
        pyperclip.copy(data)

    @staticmethod
    def cb_read():
        """
        Read data from the clipboard
        :return: data from the clipboard
        """
        return pyperclip.paste()


class EmbeddedElement:
    def __init__(self, browser: BaseWebDriver, parent: ElementAPI, page: BasePage):
        self.browser = browser
        self.parent = parent
        self.page = page

    def find(self, selector: Selector):
        for xpath in selector.xpaths:
            elements = self.parent.find_by_xpath(xpath)
            if elements:
                return elements
