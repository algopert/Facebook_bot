import re
from time import sleep

import humanfriendly
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from facebook.pages.base import BasePage, SELECTORS, EmbeddedElement


class Publications(EmbeddedElement):
    link_regex = re.compile("/\w+/posts/\d+$")

    @property
    def reaction_text(self):
        text_span = self.find(SELECTORS.reactTxt)
        if text_span:
            return text_span.text

    @property
    def reaction_count(self):
        t = self.reaction_text
        if not t:
            return 0
        try:
            return humanfriendly.parse_size(t.replace(',', '.'))
        except Exception:
            return 0

    @property
    def link(self):
        pub_link = self.find(SELECTORS.pubLink)
        self.page.hover(pub_link)
        sleep(1)
        if pub_link:
            return pub_link['href'].split("?")[0]

    @property
    def share_button(self):
        return self.find(SELECTORS.pubShrBtn)

    @property
    def share_public_button(self):
        return self.find(SELECTORS.shrPblc)

    @property
    def share_friends_button(self):
        return self.find(SELECTORS.shrFrnd)

    def share(self):
        self.share_button.click()
        sleep(3)
        # Share public if not then friends
        try:
            self.share_public_button.click()
        except:
            self.share_friends_button.click()
        # Wait for fblogo button to be clickable
        for xpath in SELECTORS.fbLogo.xpaths:
            try:
                WebDriverWait(self.browser.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            except:
                pass
        sleep(3)


class FBPage(BasePage):
    @property
    def publications(self):
        pub_list = []
        for pub in self.find(SELECTORS.pagePubs):
            pub_list.append(Publications(self.browser, pub, self))
        return pub_list

    @property
    def popup_button(self):
        return self.find(SELECTORS.popUpBtn)

    @property
    def block_button(self):
        return self.find(SELECTORS.blockBtn)

    @property
    def dblock_button(self):
        return self.find(SELECTORS.deblockBtn)

    @property
    def confirm_button(self):
        return self.find(SELECTORS.confirmBlockBtn)

    @property
    def block_modal(self):
        return self.find(SELECTORS.pageBlockDilog)

    @property
    def like_button(self):
        return self.find(SELECTORS.pageLikeButton)

    @property
    def not_reachable(self):
        return self.find(SELECTORS.pageNotReachable)

    @property
    def broken_page(self):
        return self.find(SELECTORS.brknPage)

    def block_page(self):
        self.is_present(SELECTORS.blockBtn, 2)
        sleep(1)
        self.block_button.click()
        sleep(1)
        self.is_present(SELECTORS.pageBlockDilog, 2)
        sleep(1)
        self.confirm_button.click()

