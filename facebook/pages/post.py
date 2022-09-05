# Todo: merge moderation logic in this page at least the basic commands for it
import difflib
import re
import string
from random import choice
from time import sleep
from typing import List

from selenium.webdriver.common.keys import Keys

from exceptions import AlreadyReactedError, LoopingExpanders, InvalidComment
from facebook.pages.base import BasePage, SELECTORS, EmbeddedElement


class Reactions:
    like = "like"
    wow = "wow"
    love = "love"


EMOJI_PATTERN = re.compile(
    '(\ud83d[\ude00-\ude4f])|(\ud83c[\udf00-\uffff])|(\ud83d[\x00-\uddff])|(\ud83d[\ude80-\udeff])|(\ud83c[\udde0-\uddff])+',
    flags=re.UNICODE)


# ToDo:
#  add react undo and comment delete for testing, after making sure the react/comment is done properly

class Comment(EmbeddedElement):
    @property
    def username(self):
        return self.find(SELECTORS.commentUser).text

    @property
    def control(self):
        return self.find(SELECTORS.visibleCommentCtrl)


class VisibleComment(Comment):
    @property
    def hide_button(self):
        return self.find(SELECTORS.hideComment)

    def hide(self):
        # hide this comment
        self.control.click()
        sleep(4)
        self.hide_button.click()


class InvisibleComment(Comment):
    @property
    def unhidden_button(self):
        return self.find(SELECTORS.unhidComment)

    def unhidden(self):
        """Make this comment visible"""
        self.unhidden_button.click()


class PostPage(BasePage):
    """
    Page opened after visiting the post url
    """

    @property
    def unavailable(self):
        return self.find(SELECTORS.postUnavailable)

    @property
    def frequent(self):
        return self.find(SELECTORS.postFrequentReactions)

    @property
    def _actor_selector(self):
        return self.find(SELECTORS.actorSelector)

    @property
    def _actor_list(self):
        return self.find(SELECTORS.actorList)

    @property
    def _reaction_button(self):
        return self.find(SELECTORS.reactBtn)

    @property
    def _like_button(self):
        return self.find(SELECTORS.likeBtn)

    @property
    def _love_button(self):
        return self.find(SELECTORS.loveBtn)

    @property
    def _wow_button(self):
        return self.find(SELECTORS.wowBtn)

    @property
    def _reacted(self):
        """ Check if required reaction element is active"""
        return bool(self.find(SELECTORS.reactedBtn))

    @property
    def _comment_box(self):
        return self.find(SELECTORS.commentBox)

    @property
    def _broken_page(self):
        return self.find(SELECTORS.brknPage)

    @property
    def _too_many_actions(self):
        return self.find(SELECTORS.tooManyActions)

    @property
    def _main_post(self):
        return self.find(SELECTORS.mainPost)

    @property
    def disabled_page(self):
        return bool(self._broken_page or not self._main_post)

    @property
    def title(self):
        return self.find(SELECTORS.postTitle).text

    @property
    def content_text(self):
        return self.find(SELECTORS.postContent).text

    @property
    def content_html(self):
        return self.find(SELECTORS.postContent)['innerHTML']

    @property
    def affected_link(self):
        return self.find(SELECTORS.apLink)

    @property
    def spam_count(self):
        return self.find(SELECTORS.spamCount)

    @property
    def hide_all_pubs_count(self):
        return self.find(SELECTORS.hide_all_pubs)

    @property
    def hide_pub_count(self):
        return self.find(SELECTORS.hide_pub)

    @property
    def disliked_page_count(self):
        return self.find(SELECTORS.disliked_page)

    @property
    def report_close_button(self):
        return self.find(SELECTORS.rptCloseBtn)

    @property
    def invisible_comments(self) -> List[InvisibleComment]:
        """Get hidden comments on the page"""
        comments = self.find(SELECTORS.invisibleComment)
        if comments:
            comment_objs = []
            for comment in comments:
                comment_objs.append(InvisibleComment(self.browser, comment, self))
            return comment_objs
        return []

    @property
    def visible_comments(self) -> List[VisibleComment]:
        """Get hidden comments on the page"""
        comments = self.find(SELECTORS.visibleComment)
        if comments:
            comment_objs = []
            for comment in comments:
                comment_objs.append(VisibleComment(self.browser, comment, self))
            return comment_objs
        return []

    @property
    def visible_responses(self) -> List[VisibleComment]:
        """Get hidden comments on the page"""
        comments = self.find(SELECTORS.visibleCommentResponse)
        if comments:
            comment_objs = []
            for comment in comments:
                comment_objs.append(VisibleComment(self.browser, comment, self))
            return comment_objs
        return []

    def get_actors_list(self):
        try:
            self._actor_selector.click()
            sleep(1)
            page_list = [page.text for page in self._actor_list]
            self._actor_selector.click()
            return page_list
        except AttributeError:
            # Return a list with None actor in case there are no pages to select from
            return [None]

    def select_actor(self, name):
        """
        Select page from the page list
        :param name:
        :return:
        """
        self._actor_selector.click()
        sleep(3)
        actor = self.find(SELECTORS.actorSelect, "####", name)
        actor.click()
        # Wait for actor list to be gone
        self.is_not_present(SELECTORS.actorList, 10)
        # A static wait for page to be loaded again
        sleep(3)

    def react(self, reaction, actor):
        """
        React to the post
        :param reaction: what to react i.e. like, love, wow
        :param actor: name of the actor to react with, only user profile can do non-like reaction
        :return: boolean reaction succeeded or not
        """
        # Select actor only if there is one to select from
        if actor is not None:
            self.select_actor(actor)
        if self._reacted:
            raise AlreadyReactedError
        if reaction == Reactions.like:
            self._reaction_button.click()
        else:
            self.hover(self._reaction_button)
            sleep(2)
            if reaction == Reactions.love:
                self._love_button.click()
            if reaction == Reactions.wow:
                self._wow_button.click()
        return self._reacted

    def comment(self, comment_text):
        """
        Comment on the post
        :return:
        """
        self._comment_box.click()
        sleep(1)
        # Send random key to the comment box
        self.send_key(choice(string.ascii_letters))
        sleep(2)
        success = 0
        copy_attempt = 0
        while True:
            # Set comment text to clipboard
            self.cb_write(comment_text)
            # paste comment text from clipboard to comment box
            self.paste_text_from_cb()
            # copy comment box text to clipboard
            self.copy_text_to_cb()
            # Read comment text from the clipboard
            text1 = self.cb_read()
            # Compare the text with emojis removed
            s = difflib.SequenceMatcher(None, EMOJI_PATTERN.sub('', comment_text), EMOJI_PATTERN.sub('', text1))
            if s.ratio() < 1.0:
                if copy_attempt < 5:
                    copy_attempt = copy_attempt + 1
                    continue
                else:
                    success = 0
                    break
            else:
                success = 1
                self.send_key(Keys.ARROW_DOWN)
                sleep(1)
                self.send_key(Keys.RETURN)
                sleep(3)
                break
        return success

    def get_spam_count(self) -> int:
        # Return spam count if any else 0, also log it to the console in the caller function
        if not self.is_present(SELECTORS.apLink, 30):
            self.logger.warning("Affected persons link not found!")
            return 255
        self.affected_link.click()
        if not self.is_present(SELECTORS.spamCount, 30):
            self.logger.warning("Spam report didn't open in time")
            return 255
        count_span = self.spam_count
        if not count_span:
            self.logger.warning("Couldn't find the spam count text")
            return 255
        count_text = count_span.text
        # Close the spam report dialog
        # self.report_close_button.click()
        return int(count_text)

    def get_post_analysis(self):
        hide_all_pubs_text = self.hide_all_pubs_count.text
        hide_pub_text = self.hide_pub_count.text
        disliked_page_text = self.disliked_page_count.text
        return int(hide_all_pubs_text), int(hide_pub_text), int(disliked_page_text)

    def get_invalid_comments(self, users: List[str]):
        invalid_comments = []
        visible_comments = self.visible_comments
        if not visible_comments:
            self.logger.info("No visible comments to hide")
        else:
            self.logger.info("Processing visible comments")
            page_title = self.title
            for comment in visible_comments:
                try:
                    username = comment.username
                    if username != page_title:
                        # Check if the users isn't in list
                        if username.lower() not in users:
                            invalid_comments.append(comment)
                except Exception:
                    pass
        return invalid_comments

    def process_invalid_comments(self, users: List[str]) -> int:
        """Hide comments that are visible but posted by users not in the users list"""
        actions = 0
        visible_comments = self.visible_comments
        if not visible_comments:
            self.logger.info("No visible comments to hide")
            return 0
        self.logger.info("Processing visible comments")
        page_title = self.title
        for comment in visible_comments:
            try:
                username = comment.username
                if username != page_title:
                    # Check if the users isn't in list
                    if username.lower() not in users:
                        # If user not in list then hide comment
                        self.highlight(comment.parent)
                        sleep(2)
                        comment.hide()
                        self.send_key(Keys.ESCAPE)
                        actions += 1
                        self.logger.info(f"{username}: Comment is now hidden")
                        sleep(4)
            except AttributeError:
                # If the comment is not there or got deleted then raise
                # if page_title != '':
                raise InvalidComment
            except Exception:
                self.logger.exception("Error occurred while processing invalid comment")
                self.send_key(Keys.ESCAPE)
                continue
        return actions

    def process_responses(self) -> int:
        actions = 0
        visible_responses = self.visible_responses
        if not visible_responses:
            self.logger.info("No visible responses")
            return 0
        self.logger.info("Processing visible responses")
        for response in visible_responses:
            try:
                username = response.username
                self.logger.info(f"Trying to hide {username}")
                self.send_key(Keys.ESCAPE)
                response.hide()
                actions += 1
                self.logger.info(f"{username}: Response is now hidden")
                sleep(4)
            except AttributeError:
                # If the comment is not there or got deleted then raise
                raise InvalidComment
            except Exception:
                self.logger.exception("Error occurred while processing invalid response")
                self.send_key(Keys.ESCAPE)
                continue
        return actions

    def get_valid_comments(self, users: List[str]):
        valid_comments = []
        invisible_comments = self.invisible_comments
        if not invisible_comments:
            self.logger.info("No invisible comments to unhidden")
        else:
            self.logger.info("Processing invisible comments")
            for comment in invisible_comments:
                try:
                    # Check if the users isn't in list
                    if comment.username.lower() not in users:
                        valid_comments.append(comment)
                except Exception:
                    pass
        return valid_comments

    def process_valid_comments(self, users: List[str]) -> int:
        """
        Unhidden comments that are invisible but posted by valid users
        """
        actions = 0
        invisible_comments = self.invisible_comments
        if not invisible_comments:
            self.logger.info("No invisible comments to unhidden")
            return 0
        self.logger.info("Processing invisible comments")
        for comment in invisible_comments:
            try:
                username = comment.username.lower()
                # Check if the users is in list
                if username in users:
                    # If user in list then unhidden comment
                    self.highlight(comment.parent)
                    sleep(2)
                    comment.unhidden()
                    self.send_key(Keys.ESCAPE)
                    actions += 1
                    self.logger.info(f"{username}: Comment is now visible")
                    sleep(4)
            except AttributeError:
                # If the comment is not there or got deleted then raise
                raise InvalidComment
            except Exception:
                self.logger.exception("Error occurred while processing valid comments")
                self.send_key(Keys.ESCAPE)
                continue
        return actions

    def expand_pagers(self):
        for _ in range(2):
            # Todo: add selectors for the dots and also all click method and click all dots/responses
            if not self.click_all(SELECTORS.postResponses):
                raise LoopingExpanders
            if not self.click_all(SELECTORS.postPagers):
                raise LoopingExpanders
