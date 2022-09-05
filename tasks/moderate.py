# Add moderation script logic here
# Add comment script logic here
from random import randint, getrandbits
from threading import Thread
from time import sleep

from api.moderate import ModerationApi
from driver import FBDriver
from exceptions import LoopingExpanders, InvalidComment, CheckPointError
from settings import LOG_PATH, MODERATION_TIMEOUT
from tasks import Task, Service
from utils import get_logger, get_api_config, create_post_url

# Setup logging

logger = get_logger('moderate', LOG_PATH)
# Setup api client
api_config = get_api_config("moderate")
api_client = ModerationApi(api_config.host, api_config.local_ip, api_config.windows_user, True)


class ModerationTask(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api: ModerationApi = self.api
        self.moderator = ''

    def moderate_comments(self, page_id, post_id, page_url, users_obj, publication_saved, profile_name):
        # post_url = create_post_url(post_id, page_id)
        # post_page = self.driver.visit_post(post_url)

        # is_business_moderation = \
        #     not post_page.is_present(SELECTORS.post_header, 15)

        # forced on 08/13/2021 because facebook have some bugs
        is_business_moderation = True

        if is_business_moderation:
            post_url = create_post_url(post_id, page_id, page_url, True)
            post_page = self.driver.visit_post(post_url)

        if post_page._too_many_actions:
            logger.error(f"Disabled moderator, too many actions: {self.moderator}")
            self.api.disable_moderator(self.moderator, 1)
            # we should kill the thread here but I don'k now how to do it
            return
        elif post_page._broken_page:
            logger.error(f"Disabled page as broken: page id > {page_id} ; post id {post_id} ; profile name: {profile_name}")
            self.api.disable_page(page_id, post_id, profile_name)
            return
        elif not post_page._main_post:
            if not is_business_moderation:
                logger.error("Disabled page as required post div not found")
                self.api.disable_page(page_id, post_id, profile_name)
                return

        if bool(getrandbits(1)):
            s_count = post_page.get_spam_count()
            logger.info(f"Spam count: {s_count}")
            if s_count != 255:
                post_analytics = post_page.get_post_analysis()
                logger.info(f"Post analytics {post_analytics}")
                self.api.save_spam_count(page_id, post_id, s_count, post_analytics[0], post_analytics[1],
                                         post_analytics[2])
            else:
                self.api.save_spam_count(page_id, post_id, 999, 999, 999,
                                         999)

        # close the report page
        spam_close_btn = post_page.report_close_button
        if spam_close_btn:
            spam_close_btn.click()
            sleep(6)

        if publication_saved == 0:
            title = post_page.title
            content = post_page.content_html
            self.api.save_publication(page_id, post_id, title, title, "na", content)
        # Scroll all dots and hidden responses
        try:
            post_page.expand_pagers()
        except LoopingExpanders:
            logger.error("Clicking on expanders may be stuck in a loop! Skipping current moderation cycle")
            return
        except InvalidComment:
            logger.error("Comment may be deleted! Skipping current moderation cycle")
            return
        users_name_list = [user["f_and_l_name"].lower() for user in users_obj]
        # unhidden_count = post_page.process_valid_comments(users_name_list)
        unhidden_count = 0
        hidden_count = post_page.process_invalid_comments(users_name_list)
        responses_count = post_page.process_responses()
        self.api.update_admin_action_count(profile_name, unhidden_count + hidden_count + responses_count)

    def process(self):
        try:
            proxy_obj = api_client.get_proxy()
            users_obj = api_client.get_userids()
            posts = api_client.get_posts(proxy_obj['chrome_profile'])
            if len(posts) > 0:
                self.moderator = proxy_obj['chrome_profile']
                logger.info(f"Current moderator is: {proxy_obj['chrome_profile']}")
                self.driver = FBDriver(proxy_obj['base_dir'], proxy_obj['chrome_profile'], logger)
                try:
                    self.driver.visit_home(True)
                except CheckPointError as e:
                    logger.exception(f'Checkpoint error, disabling moderator {proxy_obj["chrome_profile"]}')
                    logger.info(f'Checkpoint error, disabling moderator {proxy_obj["chrome_profile"]}')
                    self.api.disable_moderator(proxy_obj["chrome_profile"], 0)
                else:
                    for post in posts:
                        page_id = post['page_id']
                        post_id = post['post_id']
                        page_url = post['page_url']
                        publication_saved = post['publication_saved']
                        frequency = post['frequency']

                        # Skip moderation randomly
                        if frequency == 'lf' and randint(0, 20) != 1:
                            continue

                        while True:
                            if not api_client.get_status()[0]['status'] == 'paused':
                                break
                            logger.info("Paused. Sleeping for 10 seconds")
                            sleep(10)
                        try:
                            t = Thread(target=self.moderate_comments,
                                       args=(page_id, post_id, page_url, users_obj, publication_saved, proxy_obj['chrome_profile']))
                            # Start moderation
                            t.start()
                            # Wait for moderation to complete within timeout or terminate it
                            t.join(timeout=MODERATION_TIMEOUT)
                            # self.moderate_comments(page_id, post_id, users_obj, publication_saved)
                        # Todo: minimise the exception clause to specific ones?
                        except Exception as e:
                            logger.exception(f"Failed to moderate on {create_post_url(post_id, page_id)}")
                            self.driver.screenshot()
                            self.driver.html()
            else:
                logger.info("Nothing to moderate")
        except Exception as e:
            logger.exception("Some unhandled exception occurred!!")
            if self.driver:
                self.driver.screenshot()
                self.driver.html()
        finally:
            if self.driver:
                self.driver.quit()
            self.api.inactive()
            for i in range(15 * 60, 0, -15):
                logger.info("Next moderation will be in {} seconds".format(i))
                sleep(15)


if __name__ == "__main__":
    moderate_service = Service(logger, ModerationTask, api_client, "Moderation Script")
    moderate_service.run()
