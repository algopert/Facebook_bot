from time import sleep

from facebook.pages.base import BasePage, SELECTORS


class HomePage(BasePage):
    @property
    def email_input(self):
        return self.find(SELECTORS.email)

    @property
    def password_input(self):
        return self.find(SELECTORS.passwd)

    @property
    def login_button(self):
        return self.find(SELECTORS.login)

    def login(self, email, password):
        self.email_input.type(email)
        sleep(1.8)
        self.password_input.type(password)
        sleep(1.3)
        self.login_button.click()
