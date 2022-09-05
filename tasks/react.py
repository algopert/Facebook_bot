# Add react script logic here
import traceback
from random import randint
from time import sleep

from api import ReactionApi
from driver import FBDriver
from email_sender import send_email
from exceptions import *
from facebook.pages.post import Reactions
from settings import LOG_PATH
from tasks import Task, Service
from utils import get_logger, get_api_config

# Setup logging

logger = get_logger('react', LOG_PATH)
# Setup api client
api_config = get_api_config("react")
api_client = ReactionApi(api_config.host, api_config.local_ip, api_config.windows_user, True)


class ReactionTask(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api: ReactionApi = self.api
        self.PAGES_COUNT = 0

    @staticmethod
    def get_reaction(data):
        """"
        Get the reaction to do based on the api data
        """
        r_list = []
        for k, v in data.items():
            if v > 0:
                reaction = k.replace('s_count', '')
                r_list.append(reaction)
        return r_list

    def make_extra_like(self):
        schedules = self.api.get_extra_like()
        if schedules.get('success'):
            schedule_data = schedules['data']
            user = schedule_data['User']
            schedule = schedule_data['Schedule']
            elid = schedule_data['extra_like_details']['extra_like_id']
            self.process_schedule(schedule, user, ['like'], extra=elid)

    def publish_pages(self, driver: FBDriver):
        """
        Make sure the pages managed by the user are published
        :return:
        """
        try:
            yp = driver.visit_your_pages()
            page_links = yp.page_links
            for page_link in page_links:
                ps = driver.visit_page_settings(page_link)
                # switch to iframe as fb logic
                ps.browser.driver.switch_to.frame(ps.settings_frame._element)
                # Try to modify only if not published
                if ps.page_not_published_status:
                    result = ps.publish_page()
                    if not result:
                        logger.error("Couldn't enable page")
        except Exception:
            logger.exception("Error occurred during page publish status verification")
            # Send email for the error
            send_email(traceback.format_exc())

    def like_with_pages(self):
        logger.info("Processing like with pages")
        response = api_client.get_posts_id()
        posts_to_like = response['data']['posts_id']
        posts_to_like_encrypted = response['data']['posts_id_encrypted']
        users = api_client.get_all_user_id_by_server()
        for user in users:
            if self.PAGES_COUNT and not self.api.is_allowed:
                break

            self.api.update_pages_posts_liked(user['user_id'], 'none', 0)
            driver = None
            try:
                driver = FBDriver(user['profile_dir'], user['profilename'], logger)
                logger.info(f"User profile now: {user['profilename']}")
                driver.visit_home(False)
                yp = driver.visit_your_pages()
                page_links = yp.page_links
                # Proceed only if the profile has pages
                if page_links:
                    for i, page_link in enumerate(page_links):
                        if i == 2:
                            break
                        # Visit news feed of the current page
                        nfp = driver.visit_news_feed_page(page_link)
                        logger.info(f"On Page {page_link}news_feed")
                        self.PAGES_COUNT += 1
                        logger.info(f"Visited pages count: {self.PAGES_COUNT}")
                        sleep(10)
                        # Proceed only if there are any publications in the newsfeed
                        publications = nfp.publications
                        if publications:
                            for publication in publications:
                                try:
                                    pub_id = publication.id
                                    logger.info("Pub id: " + pub_id)
                                    if pub_id in posts_to_like or pub_id in posts_to_like_encrypted:
                                        sleep(5)
                                        logger.info(f"Matched publication id: {pub_id}")
                                        publication.like()
                                        self.api.update_pages_posts_liked(user['user_id'], page_link, pub_id)
                                except AttributeError:
                                    # Ignore pub id not found due to not all publications are not posts
                                    continue
                                finally:
                                    sleep(5)
            except Exception:
                logger.exception("Error occurred during like with pages")
            finally:
                if driver:
                    driver.quit()

    def process_schedule(self, schedule, user, reaction_list, extra=False):
        driver = FBDriver(user['profile_dir'], user['profilename'], logger)
        try:
            hp = driver.visit_home(True)
            firstname = hp.firstname_old.text if driver.old_ui else hp.firstname.text
            self.api.update_first_name(firstname, schedule["id"])
            self.api.save_ui_version(user['id'], 'old' if driver.old_ui else 'new')
            error_message = ''
            tmr = False
            try:
                post_page = driver.visit_post(schedule['post_url'])
                actors = post_page.get_actors_list()
                self.api.save_page_list(user['id'], schedule['post_url'], actors)
                if extra:
                    error_occurred = False
                    try:
                        post_page.react(Reactions.like, actors[0])

                        sleep(5)
                        if post_page.frequent:
                            self.api.save_log(user['id'], schedule['id'], "Too many reactions pop-up shown")
                            self.api.disable_user(user['id'], schedule['id'], 1)
                            logger.error("Too many reactions pop-up shown")
                            tmr = True
                    except Exception as e:
                        error_occurred = True
                        error_message = f"User: {user['id']} WAS NOT ABLE TO {Reactions.like} for post: {schedule['id']}"
                    finally:
                        if not tmr:
                            if error_occurred:
                                logger.exception(error_message)
                                self.api.save_log(user['id'], schedule['id'], error_message)
                            else:
                                logger.info(
                                    f"User {user['id']} {Reactions.like}d to post {schedule['post_url']} with id {schedule['id']} successfully")
                        self.api.update_extra_reaction(extra, schedule['id'], 0 if error_occurred else 1)
                else:
                    for i, actor in enumerate(actors):
                        try:
                            # Default reaction is like
                            reaction = Reactions.like
                            # Allow only user to do the love/wow reactions
                            if i == 0:
                                if Reactions.love in reaction_list:
                                    reaction = Reactions.love
                                elif Reactions.wow in reaction_list:
                                    reaction = Reactions.wow
                            logger.info(f"Reacting {reaction} with actor {actor} for schedule {schedule['id']}")
                            reacted = post_page.react(reaction, actor)
                            if not reacted:
                                error_message = f"User: {user['id']} WAS NOT ABLE TO {reaction} AS page ( {actor} ) for post: {schedule['id']}"
                            if actor is None:
                                for _ in range(3):
                                    self.api.update_users_posts_reaction(user['id'], schedule['id'], reaction, 0,
                                                                         '*************** Profile without pages ??? ***************')
                            # check if too many likes pop-up is shown and disable the user
                            sleep(5)
                            if post_page.frequent:
                                self.api.save_log(user['id'], schedule['id'], "Too many reactions pop-up shown")
                                self.api.disable_user(user['id'], schedule['id'], 1)
                                logger.error("Too many reactions pop-up shown")
                                tmr = True
                                # ToDo: save the image and html of the page and also log to the file
                        except AlreadyReactedError:
                            # ToDo: this error is never raised, so either raise it or check here
                            error_message = f"User {user['id']} already {reaction}d post {schedule['id']}"
                            logger.error(error_message)

                        except ProfileTemporarilyBlockedError:
                            error_message = f"User {user['id']} for post {schedule['id']} is temporarily blocked!"
                            self.api.disable_user(user['id'], schedule['id'], 1)
                        except Exception:
                            error_message = f"something unknown happened?"
                            logger.error(error_message)
                        finally:
                            # If too many reactions then break the loop immediately for this user
                            if tmr:
                                break
                            if error_message:
                                logger.exception(error_message)
                                self.api.save_log(user['id'], schedule['id'], error_message)
                            else:
                                logger.info(
                                    f"User {user['id']} {reaction}d to post {schedule['post_url']} with id {schedule['id']} successfully")
                            response = self.api.update_users_posts_reaction(user['id'], schedule['id'], reaction,
                                                                            0 if error_message else 1,
                                                                            error_message,
                                                                            actor)
                            # Break loop if api says so
                            if not response['success']:
                                break
                            # Wait before changing the actor for next reaction
                            sleep(5)
                # Page published verification
                if randint(1, 50) == 1:
                    self.publish_pages(driver)
            except PostUnavailable:
                for _ in range(3):
                    if extra:
                        self.api.update_extra_reaction(extra, schedule['id'], 0)
                    else:
                        self.api.update_users_posts_reaction(user['id'], schedule['id'], reaction_list[0], 0,
                                                             'Content is unavailable')

        except CheckPointError as e:
            self.api.disable_user(user['id'], schedule['id'])
            for _ in range(3):
                if extra:
                    self.api.update_extra_reaction(extra, schedule['id'], 0)
                else:
                    self.api.update_users_posts_reaction(user['id'], schedule['id'], reaction_list[0], 0,
                                                         'Checkpoint Error')
            logger.exception(f'Checkpoint error, disabling user {user["id"]} {schedule["id"]}')
            raise e
        except Exception as e:
            raise e
        finally:
            driver.quit()

    def process(self):
        schedules = api_client.get_schedules()
        if schedules['success']:
            if schedules['data'] == "pages":
                self.like_with_pages()
            else:
                self.make_extra_like()
                # Let the api server know we are processing the schedule
                logger.info('users_posts_liked {}'.format(schedules))
                logger.info('Commands: {}'.format(schedules['data']['UsersPostsLiked']))
                schedule_data = schedules['data']
                user = schedule_data['User']
                schedule = schedule_data['Schedule']
                # unliked_pages = schedule_data['UnlikedPages']
                reaction_list = self.get_reaction(schedule_data['UsersPostsLiked'])
                logger.debug(reaction_list)
                self.process_schedule(schedule, user, reaction_list)


if __name__ == "__main__":
    react_service = Service(logger, ReactionTask, api_client, "Likes Script")
    react_service.run()
