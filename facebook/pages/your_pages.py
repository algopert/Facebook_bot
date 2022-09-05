from facebook.pages.base import BasePage, SELECTORS


class YourPages(BasePage):
    @property
    def page_links(self):
        links = []
        link_elements = self.find(SELECTORS.page_links)
        if link_elements:
            for link_element in link_elements:
                links.append(link_element['href'].replace('?ref=pages_you_manage', ''))
        return links
