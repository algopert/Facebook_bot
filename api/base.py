import logging

import requests


class Api:
    def __init__(self, host, local_ip, windows_user, enabled=False):
        self.BASE_URL = f"{host}/api"
        self.local_ip = local_ip
        self.logger = logging.getLogger()
        self.enabled = enabled
        self.windows_user = windows_user

    def get(self, endpoint, **kwargs):
        try:
            return requests.get(f"{self.BASE_URL}{endpoint}", **kwargs)
        except Exception:
            self.logger.exception('Error occurred while contacting to API sever')

    def post(self, endpoint, **kwargs):
        try:
            return requests.post(f"{self.BASE_URL}{endpoint}", **kwargs)
        except Exception:
            self.logger.exception('Error occurred while contacting to API sever')

    def update_status(self, status):
        raise NotImplemented

    def active(self):
        self.update_status(1)

    def inactive(self):
        self.update_status(0)

    def is_allowed(self) -> bool:
        raise NotImplemented
