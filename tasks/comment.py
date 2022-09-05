# Add comment script logic here
from random import choice

from api import CommentApi
from driver import FBDriver
from exceptions import CheckPointError
from settings import LOG_PATH
from settings import REACTION_LIMIT_HIGH, REACTION_LIMIT_LOW, MAX_PAGE_VISIT, MAX_PUB_SCAN
from tasks import Task, Service
from utils import get_logger, create_post_url, get_api_config

# Setup logging
logger = get_logger('comment', LOG_PATH)
# Setup api client
api_config = get_api_config("comment")
api_client = CommentApi(api_config.host, api_config.local_ip, api_config.windows_user, True)


class CommentTask(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api: CommentApi = self.api

    def share_publication_from_page(self, driver, page_link, min_reaction_count, max_posts_to_scan):
        """"
        Share publication if minimum reaction criteria is meet
        :return True if shared else None
        """
        # Go to page url
        pub_page = driver.visit_publication(page_link)
        # Scroll down a bit to more publications loaded on the page
        pub_page.scroll()
        # Get latest max_posts_to_scan publication
        publications = pub_page.publications
        # list of reaction counts of the publications
        r_counts = []
        if len(publications) > 0:
            for pub in pub_page.publications[:min(len(publications), max_posts_to_scan)]:
                # Share publication if reactions are more than 50
                r_counts.append(pub.reaction_count)
                if pub.reaction_count > min_reaction_count:
                    logger.info(f"Count: {pub.reaction_count}, Link: {pub.link}")
                    pub.share()
                    return True, r_counts
        return False, r_counts

    def share_publication(self, driver):
        profile_page = driver.visit_profile()
        liked_pages_links = profile_page.liked_pages_links
        if not liked_pages_links:
            return
        logger.debug(liked_pages_links)
        shared = False
        visited_pages = []
        for _ in range(MAX_PAGE_VISIT):
            page_link = choice(liked_pages_links)
            # Remove page from the liked_pages list
            liked_pages_links.remove(page_link)
            logger.debug(f"Selecting page {page_link}")
            shared, r_counts = self.share_publication_from_page(driver, page_link, REACTION_LIMIT_HIGH, MAX_PUB_SCAN)
            if shared:
                break
            else:
                visited_pages.append({'page_link': page_link, 'counts': max(r_counts)})
        if not shared:
            # Get the page which has required no of the counts and try to share from it
            page_link = None
            for p in visited_pages:
                if p['counts'] > REACTION_LIMIT_LOW:
                    page_link = p['page_link']
                    break
            if page_link:
                shared, _ = self.share_publication_from_page(driver, page_link, REACTION_LIMIT_LOW, MAX_PUB_SCAN)

        if shared:
            logger.debug("Post is shared , getting the link of it")
            # Go to profile page
            profile_page = driver.visit_profile()
            return profile_page.first_post_link

    def process_schedule(self, schedule):
        # logger.debug(schedule)
        post_url = create_post_url(schedule['post_id'], schedule['page_id'], 0)
        comment = self.api.get_comment_for_schedule(schedule["id"])
        logger.info(
            f'Posting comment for profile {schedule["profilename"]} schedule id {schedule["id"]} page id {schedule["page_id"]}. Attempt : {schedule["attempt"] + 1}')
        driver = FBDriver(schedule["profile_dir"], schedule["profilename"], logger)
        # logger.info(f"Comment data received: {comment}")
        try:
            try:
                hp = driver.visit_home(True)
                firstname = hp.firstname_old.text if driver.old_ui else hp.firstname.text
                self.api.update_first_name(firstname, schedule["id"])
                self.api.save_ui_version(schedule["uid"], 'old' if driver.old_ui else 'new')
                logger.debug(f"Visiting post url {post_url}")
                post_page = driver.visit_post(post_url)
                commented = post_page.comment(comment['comment'])
                # Update comment status to the api server

                self.api.update_schedule(schedule["id"], commented, schedule["attempt"])
                self.api.fail_user(schedule["uid"], 'no' if commented == 1 else 'yes')
            except CheckPointError as e:
                self.api.disable_user(schedule["uid"])
                self.api.update_schedule(schedule["id"], 0, 1)
                logger.exception(f'Checkpoint error, disabling user {schedule["uid"]} {schedule["id"]}')
                raise e
            except Exception as e:
                self.api.update_schedule(schedule["id"], 0, schedule["attempt"])
                self.api.fail_user(schedule["uid"], 'yes')
                raise e
            else:
                try:
                    if commented == 1:
                        if comment['publication_type']:
                            logger.info("Post content on wall started")
                            profile_page = driver.visit_profile()
                            content_link = profile_page.wall_post(comment['publication_file_url'],
                                                                  comment['publication_type'],
                                                                  comment['publication_text'])
                            if content_link:
                                logger.info(f"Post link: {content_link}")
                                self.api.save_new_content_url(content_link, comment['publication_id'], schedule['uid'])
                                self.api.save_report_issue(schedule["uid"], 'content_publication_success')
                            else:
                                self.api.save_report_issue(schedule["uid"], 'content_publication_fail')
                                logger.info("Content publication failed and reported")
                except Exception as e:
                    self.api.save_report_issue(schedule["uid"], 'content_publication_fail')
                    raise e
                try:
                    if comment['share_random_publication'] == 1:
                        logger.info("Share random publication started")
                        post_link = self.share_publication(driver)
                        if post_link:
                            self.api.save_publication_share(schedule["uid"], post_link)
                            self.api.save_report_issue(schedule["uid"], 'publication_sharing_success')
                            logger.info("Share random publication completed")
                        else:
                            self.api.save_report_issue(schedule["uid"], 'publication_sharing_fail')
                            logger.info("Share random publication failed and reported")
                except Exception as e:
                    self.api.save_report_issue(schedule["uid"], 'publication_sharing_fail')
                    raise e
        except Exception as e:
            logger.exception(f"Failed to comment on {post_url}")
            driver.screenshot()
            driver.html()
        finally:
            # Make sure the browser is closed after processing this schedule
            driver.quit()

    def process(self):
        schedules = api_client.get_schedules()
        for schedule in schedules:
            self.process_schedule(schedule)


if __name__ == "__main__":
    comment_service = Service(logger, CommentTask, api_client, "Comments Script")
    comment_service.run()
