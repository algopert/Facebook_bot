# encoding: utf-8
import datetime
from datetime import datetime
from time import sleep

from api import CommentApi
from driver import FBDriver
from settings import LOG_PATH
from tasks import Task, Service
from utils import get_logger, get_api_config

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

    def block_page(self, page_url, user):
        driver = FBDriver(user["profile_dir"], user["profilename"], logger)
        uid = user['id']
        try:
            driver.visit_home(False)
            logger.debug(f"Visiting page url {page_url}")
            private_page = driver.visit_publication(page_url)
            sleep(5)
            if private_page.not_reachable:
                self.api.update_block_page_by_uid(uid, 3)
                # If like button is present then try to block the page
            elif private_page.like_button:
                private_page.block_page()
                sleep(5)
                private_page.browser.reload()
                sleep(5)
                if private_page.like_button:
                    self.api.update_block_page_by_uid(uid, 1)
                else:
                    self.api.update_block_page_by_uid(uid, 2)
            sleep(5)
        except:
            pass
        finally:
            driver.quit()

    def process_page_obj(self, page_obj):
        print(page_obj)
        page_time = datetime.strptime(page_obj['date_dt'], fmt)
        # Todo: make sure to parse the page_time in datetime format first
        if datetime.now() >= page_time:
            page_url = page_obj['page_url']
            users = page_obj['users']
            for user in users:
                # Get the browser for current profile and process the block page algorithm
                self.block_page(page_url, user)

    def process(self):
        response = self.api.get_pages_to_block()
        if not response or response['status'] == False:
            print("No job to process")
            return
        print(response)
        for page_obj in response["pages"]:
            self.process_page_obj(page_obj)
            response = self.api.updated_blocked_pages(page_obj['id'])
            print(f"Response of the updated: {response}")


if __name__ == "__main__":
    page_blocker_service = Service(logger, PageBlockerTask, api_client, "Page Blocker Script")
    # To run the script only once
    page_blocker_service.task(api=page_blocker_service.api, email_client=None).process()
