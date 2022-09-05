from time import sleep

from facebook.pages.base import BasePage, SELECTORS


class PageSettings(BasePage):
    @property
    def page_not_published_status(self):
        return self.find(SELECTORS.page_not_published)

    @property
    def modify_button(self):
        return self.find(SELECTORS.page_status_modifier_button)

    @property
    def publish_radio(self):
        return self.find(SELECTORS.page_publish_radio)

    @property
    def modification_save_button(self):
        return self.find(SELECTORS.page_modification_save_button)

    @property
    def settings_frame(self):
        return self.find(SELECTORS.page_settings_iframe)

    def publish_page(self) -> bool:
        self.modify_button.click()
        self.is_present(SELECTORS.page_status_modifier_button, 20)
        sleep(5)
        self.publish_radio.click()
        sleep(5)
        self.modification_save_button.click()
        sleep(5)
        # Reload the page and verify the published status
        self.browser.reload()
        sleep(5)
        if self.page_not_published_status:
            return False
        else:
            return True
