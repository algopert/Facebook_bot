from .base import Api


class CommentApi(Api):
    def get_comment_for_schedule(self, schedule_id):
        endpoint = f"/schedules/getcomment/{schedule_id}"
        response = self.get(endpoint)
        if response:
            return response.json()

    @property
    def is_allowed(self) -> bool:
        """
        Check if script is allowed to run
        """
        endpoint = "/is_allowed_to_comment"
        response = self.get(endpoint, params={'server': self.local_ip})
        if response:
            return response.json()['success']

    def update_status(self, status):
        """
        Update script status to api server
        """
        endpoint = "/update_comment_script_status"
        response = self.get(endpoint, params={'server': self.local_ip, 'status': status})
        if response:
            return response.json()['success']

    def fail_user(self, uid, value):
        endpoint = f"/users/uid/{uid}/failed/{value}"
        response = self.get(endpoint)
        if response:
            return response.text

    def update_first_name(self, first_name, sch_id):
        endpoint = "/updatefname"
        response = self.post(endpoint, data={'sch_id': int(sch_id), 'fname': first_name})
        if response:
            return response.text

    def get_schedules(self):
        endpoint = f"/schedules/{self.local_ip}"
        response = self.get(endpoint)
        if response:
            return response.json()

    def get_status(self):
        endpoint = "/status/Comments"
        response = self.get(endpoint)
        if response:
            return response.json()

    def update_schedule(self, id, success, attempt):
        endpoint = "/schedule/update"
        response = self.post(endpoint, data={'sch_id': int(id), 'success': success, 'attempt': int(attempt) + 1})
        if response:
            return response.text

    def save_new_content_url(self, url, pub_id, uid):
        endpoint = "/save_new_content_url"
        response = self.post(endpoint, data={'url': url, 'publication_id': pub_id, 'publication_user': uid})
        if response:
            return response.text

    def disable_user(self, user_id, temporarily_disabled=0):
        endpoint = "/users/disable"
        response = self.post(endpoint, data={'uid': int(user_id), 'temporarily_disabled': int(temporarily_disabled)})
        if response:
            return response.text

    def save_publication_share(self, user_id, pub_url):
        endpoint = "/save_publication_share"
        response = self.post(endpoint, data={'user_id': int(user_id), 'sharing_publication_url': pub_url})
        if response:
            return response.text

    def save_ui_version(self, user_id, version):
        endpoint = "/save_ui_version"
        response = self.post(endpoint, data={'user_id': int(user_id), 'version': version})
        if response:
            return response.text

    def save_report_issue(self, user_id, type):
        endpoint = "/report_issue"
        response = self.post(endpoint, data={'user_id': int(user_id), 'type': type})
        if response:
            return response.text

    def get_pages_to_block(self):
        endpoint = "/get_pages_to_blockv2"
        response = self.get(endpoint + f"/{self.local_ip}")
        if response:
            return response.json()

    def updated_blocked_pages(self, page_id):
        endpoint = "/update_blocked_pages_by_server_and_id"
        response = self.get(endpoint + f"/{self.local_ip}/{page_id}")
        if response:
            return response.json()

    def update_block_pages_by_relationship(self, schedule_id, status):
        """
        Update page block status
        """
        endpoint = f"/update_blocked_pages_by_relationship"
        data = {"id": schedule_id, "status": status}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()

    def get_all_users_by_server_nfa(self):
        endpoint = "/get_all_users_by_server_nfa"
        response = self.post(endpoint, data={'server': self.local_ip})
        if response:
            return response.json()

    def get_pages_to_like_nfa(self):
        endpoint = "/get_pages_to_like_nfa"
        response = self.get(endpoint)
        if response:
            return response.json()
