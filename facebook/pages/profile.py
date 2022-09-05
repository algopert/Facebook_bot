import os
import urllib.request
from time import sleep

from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver import ActionChains

from facebook.pages.base import BasePage, SELECTORS


class ProfilePage(BasePage):
    """
    Page opened after the profile button on homepage is clicked
    """

    @property
    def _woym_text_box(self):
        # whats on your mind text box
        return self.find(SELECTORS.woymTB)

    @property
    def _publish_btn(self):
        return self.find(SELECTORS.pubBtn)

    @property
    def _close_btn(self):
        return self.find(SELECTORS.closePub)

    @property
    def _media_btn(self):
        return self.find(SELECTORS.mediaBtn)

    @property
    def _file_input(self):
        return self.find(SELECTORS.fileInput)

    @property
    def home_button(self):
        return self.find(SELECTORS.fbHome)

    @property
    def first_post_link_span(self):
        return self.find(SELECTORS.fPostSpan)

    @property
    def first_post_link(self):
        link = self.find(SELECTORS.fPostLink)
        if link:
            self.hover(link)
            sleep(1)
            return link['href']
            # link.click()
            # sleep(5)
            # self.is_clickable(SELECTORS.profileBtn)
            # return self.browser.url

    @property
    def first_post_content(self):
        return self.find(SELECTORS.postContent).text.strip()

    @property
    def liked_pages_links(self):
        # Make sure that we are on the user likes page before getting the links
        if not self.browser.url.endswith("likes"):
            curl = self.browser.url
            # If profile id on me page url then add likes as query parameter
            if 'profile.php?id' in curl:
                likes_url = curl + '&sk=likes'
            else:
                likes_url = curl + 'likes' if curl.endswith('/') else curl + '/likes'
            self.browser.visit(likes_url)
            sleep(3)
            # Scroll to get all the liked pages
            self.scroll()

        page_links = []
        liked_pages = self.find(SELECTORS.likedPages)
        if liked_pages:
            for link in self.find(SELECTORS.likedPages):
                try:
                    page_links.append(link['href'])
                except AttributeError:
                    pass
        return page_links

    # Todo: to test this check the text of the last post returned by this function, and also the media file if any
    def wall_post(self, file_url=None, file_type=None, text=None):
        """
        Post something on user wall
        :param file_url: url to the file to upload and post on wall
        :param file_type: type of file, image/video
        :param text: text to post if any
        :return: Link to the last post which should be this one
        """
        # Todo: download the file and set filepath, remove it afterwards
        filepath = None
        if file_url:
            filename = "local-filename.jpg" if file_type == "image" else "trial_video.mp4"
            urllib.request.urlretrieve(file_url, filename)
            cwd = os.getcwd()
            filepath = os.path.join(cwd, filename)

        if not filepath and not text:
            self.logger.error("Error at least filepath or text has to provided")
            return "NA"
        # select the whats on your mind text box
        count = 30
        while count > 0:
            try:
                self._woym_text_box.click()
                break
            except ElementNotInteractableException:
                count -= 1
                sleep(2)
        if count == 0:
            self.logger.error("Unable to click on the woym text box in profile page")
            return False
        # Wait till pop up opens up upto max 5 seconds
        self.is_present(SELECTORS.closePub, 5)
        sleep(3)
        # Send the text to currently selected(automatic) text input
        if text:
            if '<br />' in text:
                text = text.replace("<br />", "\n")
            #     Todo: will this work with \n in the text?
            ActionChains(self.browser.driver).send_keys(text).perform()
            sleep(1)
        if filepath:
            # Click media upload button
            self._media_btn.click()
            sleep(3)
            # select the file to upload
            self._file_input._element.send_keys(filepath)
            sleep(3)
        # Click Publish
        self._publish_btn.click()
        # Wait for comment to publish successfully by checking the disappearance of the close button
        # Wait till pop up opens closes upto max 5 seconds
        self.is_not_present(SELECTORS.closePub, 20)
        # Wait for some time to get the timeline refreshed
        sleep(5)
        self.logger.info('Returning self post link')
        sleep(1)
        if filepath:
            os.remove(filepath)
        # Capture and return the first post link on timeline
        return self.first_post_link
