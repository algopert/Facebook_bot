# encoding: utf-8
from time import sleep

from api import CommentApi
from driver import FBDriver
from settings import LOG_PATH
from tasks import Task, Service
from utils import get_logger, get_api_config
from urllib.parse import urlparse

# Setup logging
logger = get_logger('page_blocker', LOG_PATH)
# Setup api client
api_config = get_api_config("comment")
api_client = CommentApi(api_config.host, api_config.local_ip, api_config.windows_user, True)
fmt = "%Y-%m-%d %H:%M:%S"


class PageBlockerTask(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api: CommentApi = self.api

    def block_page(self, driver, user, schedule):
        schedule_id = schedule['id']
        page_url = schedule['url']
        logger.debug(f"Schedule: {schedule} User:{user}")
        try:
            logger.debug(f"Visiting page url {page_url}")
            private_page = driver.visit_publication(page_url)
            sleep(1)
            # If page is not reachable then send 4 (fail) and return
            if private_page.broken_page or private_page.not_reachable:
                self.api.update_block_pages_by_relationship(schedule_id, 4)
                sleep(1)
                return

            # If like button is present then try to block the page
            private_page.popup_button.click()
            sleep(1)
            if private_page.dblock_button:
                self.api.update_block_pages_by_relationship(schedule_id, 1)
            elif private_page.block_button:
                private_page.block_page()
                sleep(3)

                # situation 1 (a and b)
                # after blocking the page, facebook will visit the profile setting page
                # ex: https://www.facebook.com/settings/?blocked_uid=100083405164992&tab=blocking
                # or it will go to the same page and displays the message the page is not accessible
                browser_url = driver.get_current_url()
                if private_page.broken_page or urlparse(browser_url).path == '/settings/':
                    self.api.update_block_pages_by_relationship(schedule_id, 1)
                else:
                    # situation 2
                    # If block button still present after block and page refresh then send 4 (fail) else 1 (success)
                    private_page.browser.reload()
                    sleep(5)
                    private_page.popup_button.click()
                    sleep(3)
                    if private_page.block_button:
                        self.api.update_block_pages_by_relationship(schedule_id, 4)
                    else:
                        self.api.update_block_pages_by_relationship(schedule_id, 1)
            else:
                self.api.update_block_pages_by_relationship(schedule_id, 1)
            sleep(5)
        except:
            logger.exception(f"Error occurred during schedule {schedule_id}")

    def block_pages(self, user, schedules):
        driver = FBDriver(user["profile_dir"], user["profilename"], logger)
        try:
            driver.visit_home(False)
            for schedule in schedules:
                self.block_page(driver, user, schedule)
        except Exception:
            logger.exception(f"Error occurred for user {user['id']} - {user['profilename']}")
        finally:
            driver.quit()

    def process(self):
        response = self.api.get_pages_to_block()
        if not response or response['status'] == False:
            logger.info("No job to process")
            return
        logger.debug(response)
        users = response['data']['users'].values()
        relationships = response['data']['relationships']
        links = response['data']['links']
        for user in users:
            # Get pages to block with the schedule_id
            schedules = relationships[user['id']]
            for schedule in schedules:
                schedule['url'] = links[schedule['page_id']]
            self.block_pages(user, schedules)


if __name__ == "__main__":
    page_blocker_service = Service(logger, PageBlockerTask, api_client, "Page Blocker Script")
    # To run the script only once
    page_blocker_service.task(api=page_blocker_service.api, email_client=None).process()
