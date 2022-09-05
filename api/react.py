from .base import Api


class ReactionApi(Api):
    def get_selectors(self, language):
        """
        Get element selectors
        :param language: language of the selectors
        :return: xpathobject
        """
        endpoint = f"/elements/lang/{language}"
        response = self.get(endpoint)
        if response:
            xpathObj = {}
            for xpath in response.json():
                xpathObj[xpath['ename']] = xpath['evalue']
            return xpathObj

    @property
    def is_allowed(self):
        """
        Check if script is allowed to run
        """
        if not self.enabled:
            return True
        endpoint = "/is_allowed_to_like"
        response = self.get(endpoint, params={'server': self.local_ip})
        if response:
            return response.json()['success']

    def update_pages_posts_liked(self, uid, page_link, pub_id):
        """
        Send to api which user page liked a publication
        """
        endpoint = "/update_pages_posts_liked"
        self.post(endpoint, data={'user_id': uid, 'page_name': page_link, 'publication_url': pub_id})

    def update_status(self, status):
        """
        Update script status to api server
        """
        endpoint = "/update_like_script_status"
        response = self.get(endpoint, params={'server': self.local_ip, 'status': status})
        if response:
            return response.json()['success']

    def disable_user(self, uid, sid, temporarily_disabled=0):
        """Disable user"""
        endpoint = "/users/disable"
        response = self.post(endpoint, data={'uid': uid, 'temporarily_disabled': temporarily_disabled})
        if response:
            if temporarily_disabled:
                error_message = f"Auto disabling {uid} TEMPORARILY"
            else:
                error_message = f"Auto disabling {uid}"
            self.save_log(uid, sid, error_message)
            return response.json()

    def save_page_list(self, uid, purl, pages):
        """
        Save pages available in the user profile
        :param uid: user id
        :param purl: post url where this info was collected
        :param pages: list of page name
        :return:
        """
        # ToDo: This endpoint is returning 500
        endpoint = "/save_pages_list"
        response = self.post(endpoint, data={'user_id': uid, 'post_url': purl,
                                             'pages': ','.join(pages) if pages != [None] else ''})
        if response:
            return response.json()

    def get_schedules(self, uid=0, sid=0):
        """
        Get schedule for the current server
        :param uid: user id
        :param sid: schedule id
        :return: list of liked pages
        """
        endpoint = "/get_users_posts_liked"
        response = self.post(endpoint, params={'server': self.local_ip, 'user_id': uid, 'schedule_id': sid})
        if response:
            return response.json()

    def get_extra_like(self):
        """
        Get schedule for extra like
        :return: list of liked pages
        """
        endpoint = "/get_extra_like"
        response = self.post(endpoint, params={'server': self.local_ip})
        if response:
            return response.json()

    def update_users_posts_reaction(self, uid, sid, reaction, success=1, message='', pname=''):
        """
        Update reaction command success or failure with message
        :param uid: user id
        :param sid: schedule id
        :param reaction: reaction performed
        :param success: reaction registered or not
        :param message: error if reaction not registered
        :param pname: page name which reacted to the post
        :return:
        """
        endpoint = "/update_users_posts_liked"
        response = self.post(endpoint, params={'server': self.local_ip, 'user_id': uid, 'schedule_id': sid,
                                               f'{reaction}s': success,
                                               'errors': 0 if success == 1 else 1, 'message': message,
                                               'page_name': pname})
        if response:
            return response.json()

    def update_extra_reaction(self, extra_like_id, sid, success=1):
        """
        Update extra like command success or failure
        :param extra_like_id: special id
        :param sid: schedule id
        :param success: like registered or not
        :return:
        """
        endpoint = "/update_users_posts_liked"
        response = self.post(endpoint,
                             params={'extra_like_id': extra_like_id, 'success': success, 'schedule_id': sid, })
        if response:
            return response.json()

    def update_page_like(self, purl, pname):
        # ToDo: don't know what db changes should be there, returning success False
        endpoint = "/update_page_like"
        response = self.post(endpoint, params={'post_url': purl, 'page': pname})
        if response:
            return response.json()

    def update_publication_count(self, uid, sid, rcount):
        """
        Update publication reactions count
        :return:
        """
        endpoint = "/update_publication_count"
        response = self.post(endpoint, params={'server': self.local_ip, 'user_id': uid, 'schedule_id': sid,
                                               'reaction_count': rcount})
        if response:
            return response.json()

    def save_log(self, uid, sid, message):
        """
        Send logs to the server
        :return:
        """
        endpoint = "/add_log"
        response = self.post(endpoint,
                             params={'server': self.local_ip, 'user_id': uid, 'schedule_id': sid, 'message': message})
        if response:
            return response.json()

    def update_first_name(self, first_name, sch_id):
        endpoint = "/updatefname"
        response = self.post(endpoint, data={'sch_id': int(sch_id), 'fname': first_name})
        if response:
            return response.text

    def save_ui_version(self, user_id, version):
        endpoint = "/save_ui_version"
        response = self.post(endpoint, data={'user_id': int(user_id), 'version': version})
        if response:
            return response.text

    def get_posts_id(self):
        endpoint = "/get_posts_id"
        response = self.get(endpoint)
        if response:
            return response.json()

    def get_all_user_id_by_server(self):
        endpoint = "/get_all_users_id_by_server"
        response = self.post(endpoint, data={'server': self.local_ip})
        if response:
            return response.json()
