from .base import Api


# noinspection PyUnresolvedReferences
class ModerationApi(Api):
    def get_selectors(self, language):
        """
        Get element selectors
        :param language: language of the selectors
        :return: xpathobject
        """
        endpoint = f"/elements/type/1/lang/{language}"
        response = self.get(endpoint)
        if response:
            xpathObj = {}
            for xpath in response.json():
                xpathObj[xpath['ename']] = xpath['evalue']
            return xpathObj

    def get_scam_words(self):
        """
        Get element selectors
        """
        endpoint = f"/get_scam_words"
        response = self.get(endpoint)
        if response:
            return response.json()

    def update_status(self, status):
        """
        Get element selectors
        :param status: status of the script
        """
        endpoint = f"/update_moderation_script_status"
        response = self.get(endpoint, params={'server': self.local_ip, 'status': status})
        if response:
            return response.json()

    def get_status(self):
        """
        Get moderation status
        """
        endpoint = f"/status/Moderator"
        response = self.get(endpoint)
        if response:
            return response.json()

    def get_proxy(self):
        """
        Get proxy object
        """
        endpoint = f"/get_admin_proxy/{self.local_ip}/{self.windows_user}"
        response = self.get(endpoint)
        if response:
            return response.json()

    def get_userids(self):
        """
        Get userids
        """
        endpoint = f"/get_all_users_id"
        response = self.get(endpoint)
        if response:
            return response.json()

    def get_posts(self, profile):
        """
        Get posts for the profile
        """
        endpoint = f"/posts/{profile}"
        response = self.get(endpoint)
        if response:
            return response.json()

    def save_publication(self, page_id, post_id, title, author, post_time, text):
        """
        Get posts for the profile
        """
        endpoint = f"/save_publication"
        data = {"page_id": page_id, "post_id": post_id, "title": title, "author": author, "post_time": post_time,
                "text": text}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()

    @property
    def is_allowed(self):
        """
        Check if script is allowed to run
        """
        endpoint = f"/is_allowed_to_moderate"
        try:
            response = self.get(endpoint, params={'server': self.local_ip})
            if response:
                return response.json()['success']
        except Exception:
            print("API ERROR ON is_allowed()")
            return False

    def save_spam_count(self, page_id, post_id, spam_count, hap, hp, dp):
        """
        Save spam count of the post
        """
        endpoint = f"/save_spam_count"
        data = {"page_id": page_id, "post_id": post_id, "spam_count": spam_count, "hide_all_pubs": hap, "hide_pub": hp,
                "disliked_page": dp}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()

    def disable_page(self, page_id, post_id, profile_name):
        """
        Disable page
        """
        endpoint = f"/disable_post_by_page_id_and_post_id_and_profile_name"
        data = {"page_id": page_id, "post_id": post_id, "profile_name": profile_name}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()

    def disable_moderator(self, chrome_profile, temporary):
        """
        Disable moderator
        """
        endpoint = f"/disable_moderator_by_chrome_profile"
        data = {"chrome_profile": chrome_profile, "temporary": temporary}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()

    def update_admin_action_count(self, profile_name, count):
        """
        Update Admin actions count
        """
        endpoint = f"/update_admin_action_count"
        data = {"profile_name": profile_name, "count": count, 'server': self.local_ip}
        response = self.post(endpoint, data=data)
        if response:
            return response.json()
