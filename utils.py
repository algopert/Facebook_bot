import logging
import os
from logging.handlers import RotatingFileHandler

import psutil
from selenium.webdriver import ChromeOptions
from splinter.browser import ChromeWebDriver
from splinter.driver.webdriver import BaseWebDriver
from webdriver_manager.chrome import ChromeDriverManager

from common import HOME_URL, BUSINESS_URL
from settings import LOCAL_IP, WINDOWS_USER, COMMENT_HOST, REACT_HOST, MODERATE_HOST

# Check the chromedriver once on import
ep = ChromeDriverManager().install()


def kill_chrome_brower_with_profile(profile_name):
    """
    Helper function to kill chrome process for specific profile
    :param profile_name: name of the chrome profile
    :return: None
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == "chrome.exe":
                for args in proc.cmdline():
                    if args == f'--profile-directory={profile_name}':
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def get_browser(profile_dir=None, profile_name=None) -> BaseWebDriver:
    """
    Helper function to start a new chrome instance optionally with given profile info
    :param profile_dir: base directory of the profile
    :param profile_name: name of the profile to open
    :return: splinter chrome driver instance
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-infobars")
    # To hide navigator property
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    if profile_dir:
        chrome_options.add_argument(f'user-data-dir={profile_dir}')
    if profile_name:
        # Kill any existing chrome instance running for the same profile
        kill_chrome_brower_with_profile(profile_name)
        chrome_options.add_argument(f'profile-directory={profile_name}')
    browser = ChromeWebDriver(options=chrome_options, executable_path=ep)
    # Make browser fullscreen to fit whatever is the screen size
    browser.driver.maximize_window()
    return browser


def create_post_url(post_id, page_id, page_url, is_business_moderation = False):
    """
    Create url of facebook post from it's id and page id
    :return: fb post page url
    """
    if post_id.isnumeric():
        if is_business_moderation:
            return f'{BUSINESS_URL}/permalink.php?story_fbid={post_id}&id={page_id}'
        else:
            return f'{HOME_URL}/permalink.php?story_fbid={post_id}&id={page_id}'
    else:
        if is_business_moderation:
            return f'{BUSINESS_URL}{page_url}posts/{post_id}'
        else:
            return f'{HOME_URL}{page_url}posts/{post_id}'


def get_logger(name, log_dir) -> logging.Logger:
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler()
    # 500 MB file size with 1 backup
    f_handler = RotatingFileHandler(os.path.join(log_dir, f'{name}.log'), mode='a', maxBytes=500 * 1024 * 1024,
                                    backupCount=2)
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    return logger


class APIConfig:
    def __init__(self, host):
        self.host = host
        self.local_ip = LOCAL_IP
        self.windows_user = WINDOWS_USER


def get_api_config(task_name):
    if task_name == "comment":
        return APIConfig(COMMENT_HOST)
    elif task_name == "react":
        return APIConfig(REACT_HOST)
    elif task_name == "moderate":
        return APIConfig(MODERATE_HOST)
    else:
        print("Please correct the task name")
        return None
