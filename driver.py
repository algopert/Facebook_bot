import os
from datetime import datetime
from time import sleep
from urllib.parse import urlparse

from common import HOME_URL, SELECTORS, YOUR_PAGES_URL, PROFILE_URL
from exceptions import *
from facebook import HomePage, PostPage, ProfilePage, FBPage, YourPages, PageSettings
from facebook.pages.news_feed import NewsFeedPage
from settings import SCREENSHOTS_PATH
from utils import get_browser


# Todo: could use differnet types of error instead of common one?

class FBDriver:
    def __init__(self, profile_dir, profile_name, logger):
        # Todo: handle some errors here for invocation troubles?
        self.browser = get_browser(profile_dir, profile_name)
        self.profile_name = profile_name
        self.logger = logger
        self.old_ui = False

    def get_current_url(self):
        return self.browser.url

    def html(self):
        html_file = os.path.join(SCREENSHOTS_PATH,
                                 f"{self.profile_name}-{datetime.now().isoformat()}.html".replace(":", "-"))
        with open(html_file, 'w', encoding="utf-8") as fp:
            fp.write(self.browser.html)
        self.logger.error(f'HTML saved to the {html_file}.')
        return html_file

    def screenshot(self):
        screenshot_name = os.path.join(SCREENSHOTS_PATH,
                                       f"{self.profile_name}-{datetime.now().isoformat()}.png".replace(":", "-"))

        screenshot_file = self.browser.screenshot(screenshot_name)
        self.logger.error(f'Screenshot saved to the {screenshot_file}.')
        return screenshot_file

    def get(self, url):
        self.logger.info(f"\n{'-' * 80}\nURL Launching: {url} \n{'-' * 80}")
        self.browser.visit(url)
        # Check if there is any network error by checking chrome error page code
        http_error = self.browser.find_by_css('#error-information-popup-content div.error-code')
        if http_error:
            error_code = http_error.text
            msg = f'Network Error: {error_code} while parsing: s{url}'
            self.logger.error(msg)
            raise NetworkError(msg)

        browser_url = self.browser.url
        # Check if we have a checkpoint error
        if "/checkpoint/" in browser_url:
            raise CheckPointError
        # Check that the requested url path and visited url path is same, ignore the query part
        if urlparse(browser_url).path != urlparse(url).path:
            msg = f"Requested url {url} does not match with loaded url {browser_url}"
            self.logger.error(msg)
            raise UrlMisMatchError(msg)
        self.logger.info(f"{'-' * 80}\nURL Launched: {url} \n{'-' * 80}")

    def visit_home(self, scroll=False) -> HomePage:
        while True:
            try:
                self.get(HOME_URL)
                break
            except NetworkError:
                raise NetworkError
            except:
                continue

        # Todo: should this be compatible with old ui as well?
        hp = HomePage(self.browser, self.logger)
        # if hp.firstname_old:
        #     self.old_ui = True
        # elif hp.firstname:
        #     self.old_ui = False
        # else:
        #     # Raise error if none of the UI version is detected
        #     raise NotLoggedIn(f"User with profile {self.profile_name} is not logged in!")
        self.old_ui = False
        if scroll:
            hp.scroll_randomly()
        return hp

    def visit_profile(self) -> ProfilePage:
        """Visit user profile page"""
        pp = ProfilePage(self.browser, self.logger)
        # pp.profile_button.click()
        # Instead of clicking on the profile button visit the profile url
        try:
            self.get(PROFILE_URL)
        except UrlMisMatchError:
            # Silently pass url mismatch error as it's going to redirect to user page internally
            pass
        # Let the profile page load
        sleep(5)
        pp.is_clickable(SELECTORS.woymTB, 30)
        sleep(3)
        return pp

    def visit_post(self, url) -> PostPage:
        # Todo: do some verification on the post url format?
        self.get(url)
        pp = PostPage(self.browser, self.logger)
        if pp.unavailable:
            raise PostUnavailable(f"Post at url {url} is not available")
        return PostPage(self.browser, self.logger)

    def visit_publication(self, url) -> FBPage:
        # Todo: do some verification on the publication url format?
        self.get(url)
        return FBPage(self.browser, self.logger)

    def visit_your_pages(self):
        self.get(YOUR_PAGES_URL)
        return YourPages(self.browser, self.logger)

    def visit_page_settings(self, page_url):
        self.get(page_url + 'settings/?tab=settings')
        return PageSettings(self.browser, self.logger)

    def quit(self):
        try:
            self.browser.quit()
        except:
            pass

    def visit_news_feed_page(self, page_link):
        self.get(page_link + "news_feed")
        sleep(5)
        # Check for the new feed enable dialog and process it
        suivant_xpath = '//div[@aria-label="Suivant"]'
        if self.browser.find_by_xpath(suivant_xpath):
            for i in range(3):
                suivant = self.browser.find_by_xpath(suivant_xpath)
                if suivant:
                    self.logger.info(f"Clicking on next button, counter: {i + 1}")
                    suivant[i].click()
                    sleep(5)

            self.logger.info("Clicking on the accept news feed button")
            # Click on accept newsfeed
            self.browser.find_by_xpath('//span[text()="Accéder au fil d’actualité"]').click()
            sleep(10)
        return NewsFeedPage(self.browser, self.logger)
