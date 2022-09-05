# Add react script logic here
from time import sleep
from urllib.parse import urljoin

from splinter.exceptions import ElementDoesNotExist

from api import CommentApi
from common import HOME_URL, Selector
from driver import FBDriver
from facebook.pages.home import HomePage
from settings import LOG_PATH
from utils import get_logger, get_api_config

# Setup logging

logger = get_logger('news_feed_automation', LOG_PATH)
api_config = get_api_config("comment")
api_client = CommentApi(api_config.host, api_config.local_ip, api_config.windows_user, True)

PAGES_COUNT = 0


def process_single_page_like(driver):
    # Click on 3 dots
    logger.info("Clicking on 3 dots")
    driver.browser.find_by_xpath('//div[@aria-label="Autres actions"]').click()
    sleep(5)
    logger.info("Clicking on like as page")
    driver.browser.find_by_xpath('//span[text()="Aimer en tant que votre Page"]/../../../..').click()
    # wait for the page selection dialog to appear
    logger.info("awaiting page selection dialog appearance")
    hp = HomePage(driver.browser, driver.logger)
    hp.is_present(Selector(('//span[text()="Aimer en tant que votre Page"]',), 'bla bla'), 15)
    # click on select a page
    logger.info("Clicking on select a page")
    driver.browser.find_by_xpath('//span[text()="Select a Page"]').click()
    sleep(5)
    logger.info("Clicking on first page selection option")
    driver.browser.find_by_xpath('//div[@class="l9j0dhe7" and @role="menu"]//div[@role="menuitemradio"]').click()
    sleep(5)
    logger.info("Clicking on the envoyer button")
    driver.browser.find_by_xpath('//div[@aria-label="Envoyer"]').click()
    sleep(5)


def visit_all_pages_newsfeed(driver):
    global PAGES_COUNT
    # Go to profile pages
    yp = driver.visit_your_pages()
    page_links = yp.page_links
    for i, page_link in enumerate(page_links):
        if i == 2:
            break
        # Visit news feed of the current page
        driver.browser.visit(page_link + "news_feed")
        logger.info(f"On Page {page_link}news_feed")
        PAGES_COUNT += 1
        logger.info(f"Visited pages count: {PAGES_COUNT}")
        sleep(5)
        logger.info("Checking for the news feed enable dialog")
        # Check for the new feed enable dialog and process it
        suivant_xpath = '//div[@aria-label="Suivant"]'
        if driver.browser.find_by_xpath(suivant_xpath):
            for i in range(3):
                suivant = driver.browser.find_by_xpath(suivant_xpath)
                if suivant:
                    logger.info(f"Clicking on next button, counter: {i + 1}")
                    suivant[i].click()
                    sleep(5)

            logger.info("Clicking on the accept news feed button")
            # Click on accept newsfeed
            driver.browser.find_by_xpath('//span[text()="Accéder au fil d’actualité"]').click()
            sleep(10)


# Main code
def main():
    fb_page_links = api_client.get_pages_to_like_nfa()['data']['pages_url']
    user_profiles = api_client.get_all_users_by_server_nfa()
    for user in user_profiles:
        driver = FBDriver(user['profile_dir'], user['profilename'], logger)
        try:
            logger.info(f"User profile now: {user['profilename']}")
            # Visit home page, don't scroll
            driver.visit_home(False)
            # yp = driver.visit_your_pages()
            # page_links = yp.page_links
            # Make sure the profile has any pages
            # if page_links:
                # Visit each fb page
            for page_link in fb_page_links:
                full_url = urljoin(HOME_URL, page_link)
                driver.get(full_url)
                logger.info(f"Visited {full_url}")
                try:
                    for i in range(2):
                        process_single_page_like(driver)
                except ElementDoesNotExist:
                    pass

            #visit_all_pages_newsfeed(driver)
        except Exception:
            logger.exception("Error occurred during newsfeed automation")
        finally:
            driver.quit()


if __name__ == "__main__":
    main()
