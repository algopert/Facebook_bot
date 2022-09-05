import ctypes
import logging
import os
from time import sleep

from api import Api


class Task:
    def __init__(self, api: Api, email_client=None):
        self.api = api
        self.email = email_client
        self.driver = None

    def process(self):
        raise NotImplemented


class Service:
    def __init__(self, logger: logging.Logger, task: Task.__class__, api: Api, title: str, email_client=None):
        self.task = task
        self.api = api
        self.email = email_client
        self.logger = logger
        self.title = title

    def run(self):
        # Set command prompt header on windows os
        if os.name == "nt":
            ctypes.windll.kernel32.SetConsoleTitleA(self.title.encode("ascii"))
        while True:
            try:
                if not self.api.is_allowed:
                    self.logger.info(f"Not allowed")
                else:
                    self.api.active()
                    self.task(api=self.api, email_client=self.email).process()
                self.api.inactive()
            except KeyboardInterrupt:
                self.logger.info("Exiting on keyboard CTRL+C request")
                break
            except Exception:
                self.logger.exception(f"Some unexpected error occurred in the {self.task.__class__.__name__}")
                #     Todo: also log to the email using email client?
            finally:
                sleep(15)
