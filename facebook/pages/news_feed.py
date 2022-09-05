from time import sleep
from urllib.parse import parse_qs, urlparse

from facebook.pages.base import BasePage, SELECTORS, EmbeddedElement


class NewFeedPublications(EmbeddedElement):
    @property
    def link(self):
        pub_link = self.find(SELECTORS.pubLink)
        self.page.hover(pub_link)
        sleep(1)
        if pub_link:
            return pub_link['href']

    @property
    def react_button(self):
        return self.find(SELECTORS.nf_react_btn)

    @property
    def _reacted(self):
        """ Check if required reaction element is active"""
        return bool(self.find(SELECTORS.nf_reacted_btn))

    def like(self):
        # If not like already then only like
        if not self._reacted:
            # raise AlreadyReactedError
            self.react_button.click()

    @property
    def id(self):
        pub_link = self.link
        try:
            pub_id = parse_qs(urlparse(pub_link).query)['story_fbid'][0]
        except KeyError:
            pub_id = urlparse(pub_link).path.split('/')[-1]
        return pub_id


class NewsFeedPage(BasePage):
    @property
    def publications(self):
        pub_list = []
        pubs = self.find(SELECTORS.pagePubs)
        if pubs:
            for pub in pubs:
                pub_list.append(NewFeedPublications(self.browser, pub, self))
        return pub_list
