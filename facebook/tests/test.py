#   Todo:
#       if possible use single profile for all the tests
#       test home page with login dialog and without it, make sure the selectors work fine and related pages are loaded correctly
#       profile page: get liked pages links, non zero for mercer profile, new post with text, with video, with both works fine
#       publication: reaction of all types works, comments also work, sharing a pub works with all the other steps before it in unit cases
import json
from time import sleep
from unittest import TestCase
from urllib.parse import urlparse

from common import HOME_URL, SELECTORS
from facebook import HomePage, ProfilePage, FBPage, PostPage, Reactions
from utils import get_browser

TEST_DATA = json.load(open("config.json"))


class TestBasePage(TestCase):
    def test_scrolling(self):
        url = "https://splinter.readthedocs.io/en/latest/index.html"
        b = get_browser()
        b.visit(url)
        hp = HomePage(b)
        self.assertEqual(b.execute_script("return window.pageYOffset"), 0)
        # Scroll twice 400 px
        hp.scroll(2)
        self.assertEqual(b.execute_script("return window.pageYOffset"), 800)
        hp.scroll_top()
        self.assertEqual(b.execute_script("return window.pageYOffset"), 0)
        hp.scroll_randomly()
        self.assertTrue(b.execute_script("return window.pageYOffset") > 400)
        b.quit()

    def test_hover(self):
        pass

    def test_presence(self):
        pass

    def test_highlight(self):
        pass

    def test_click_all(self):
        pass

    def test_browser_copy_paste(self):
        pass

    def test_clipboard_copy_paste(self):
        pass


class TestHomePage(TestCase):
    def test_selectors(self):
        b = get_browser()
        b.visit(HOME_URL)
        hp = HomePage(b)
        self.assertEqual(len(hp.email_input), 1)
        self.assertEqual(len(hp.password_input), 1)
        self.assertEqual(len(hp.login_button), 1)
        b.quit()

    def test_login(self):
        # Make sure this is executed only after the above test
        # Need username and password for this to work
        # type in the creds and check for the home page selectors like firstname or profile link
        pass


class TestProfilePage(TestCase):
    def setUp(self) -> None:
        # Initiate the browser and go to the profile page
        self.browser = get_browser(TEST_DATA["profile_dir"], TEST_DATA["profile_name"])
        self.pp = ProfilePage(self.browser)
        self.browser.visit(HOME_URL)
        self.pp.profile_button.click()
        self.pp.is_clickable(SELECTORS.woymTB, 30)
        sleep(3)

    def test_wall_post_text(self):
        post_content = TEST_DATA["self_post_text"]
        post_link = self.pp.wall_post(text=post_content)
        self.browser.reload()
        self.assertEqual(self.pp.first_post_link, post_link)

    def test_wall_post_media(self):
        # A media file is necessary for this test in the resources folder
        post_link = self.pp.wall_post(file_url=TEST_DATA["self_post_media_path"], file_type=TEST_DATA["self_post_type"],
                                      text=TEST_DATA["self_post_text"])
        self.browser.reload()
        self.assertEqual(self.pp.first_post_link, post_link)
        self.assertEqual(self.pp.first_post_content, post_link)
        # Todo: how to verify the video content?

    def test_liked_pages_links(self):
        self.assertTrue(len(self.pp.liked_pages_links) > 0)

    def tearDown(self) -> None:
        self.browser.quit()


class TestPublicationPage(TestCase):
    def setUp(self) -> None:
        # Initiate the browser and go to the profile page
        self.browser = get_browser(TEST_DATA["profile_dir"], TEST_DATA["profile_name"])
        self.browser.visit(HOME_URL)
        sleep(3)
        self.browser.visit(TEST_DATA["fbpage_url"])
        self.fp = FBPage(self.browser)
        sleep(3)

    def test_share_publication(self):
        publications = self.fp.publications
        self.assertTrue(len(publications) > 0)
        first_pub = publications[0]
        self.assertIsNotNone(first_pub.reaction_text)
        self.assertTrue(first_pub.reaction_count > 0)
        pub_url = first_pub.link
        self.assertIsNotNone(first_pub.link_regex.match(urlparse(pub_url).path))
        first_pub.share()

    def tearDown(self) -> None:
        self.browser.quit()


class TestPostPage(TestCase):
    def setUp(self) -> None:
        # Initiate the browser and go to the profile page
        self.browser = get_browser(TEST_DATA["profile_dir"], TEST_DATA["profile_name"])
        self.browser.visit(HOME_URL)
        sleep(3)
        self.browser.visit(TEST_DATA["post_url"])
        self.pp = PostPage(self.browser)
        sleep(3)
        self.actors = self.pp.get_actors_list()

    def test_get_actors_list(self):
        self.assertEqual(self.actors, TEST_DATA["actor_list"])

    # Do only one embedded reactions as doing multiple reactions could lead to an error
    def test_reaction(self):
        self.assertFalse(self.pp._reacted)
        self.pp.react(Reactions.wow, self.actors[0])
        self.assertTrue(self.pp._reacted)

    def test_comment(self):
        self.assertEqual(self.pp.comment(TEST_DATA["post_comment_text"]), 1)

    # Test this only with the post that has any spam else expect failure
    def test_get_spam_count(self):
        self.assertTrue(self.pp.get_spam_count() > 0)

    def test_post_title(self):
        self.assertEqual(self.pp.title, TEST_DATA["post_title"])

    def test_post_content(self):
        self.assertEqual(self.pp.content_text, TEST_DATA["post_content"])

    def test_process_invalid_comments(self):
        invalid_users = TEST_DATA["users_invalid"]
        # Make sure there are visible invalid comments
        self.assertTrue(len(self.pp.get_invalid_comments(invalid_users)) > 0)
        self.pp.process_invalid_comments(invalid_users)
        # Make sure there aren't any visible invalid comments
        self.assertEqual(len(self.pp.get_invalid_comments(invalid_users)), 0)

    def test_process_valid_comments(self):
        valid_users = TEST_DATA["users_valid"]
        # Make sure there are hidden valid comments
        self.assertTrue(len(self.pp.get_valid_comments(valid_users)) > 0)
        self.pp.process_valid_comments(valid_users)
        # Make sure there aren't any hidden valid comments
        self.assertEqual(len(self.pp.get_valid_comments(valid_users)), 0)

    def tearDown(self) -> None:
        self.browser.quit()
