# Add react script logic here
from time import sleep
from urllib.parse import urlparse, parse_qs

import requests
from splinter.exceptions import ElementDoesNotExist

from api import ReactionApi
from driver import FBDriver
from settings import LOG_PATH
from utils import get_logger, get_api_config

# Setup logging

logger = get_logger('like_with_pages', LOG_PATH)
# Setup api client
api_config = get_api_config("react")
api_client = ReactionApi(api_config.host, api_config.local_ip, api_config.windows_user, True)

PAGES_COUNT = 0
# Selectors
# Get all user profiles
# open profile pages section and then to the newsfeed
# scan for the publications, if any publication matches the url provided then like it

# schedules = api_client.get_schedules()
# {"status":true,"data":{"posts_id":["281218533418138","868630213985722","257534329344359","281832406690084","119634663461381","119868873482016"]}}

# if schedules['data'] == "pages":
if True:
    response = requests.get('http://phpcomments.botobot.xyz/api/get_posts_id')
    posts_to_like = response.json()['data']['posts_id']

    url = "http://phpcomments.botobot.xyz/api/get_all_users_id_by_server"

    payload = {'server': '192.236.177.107_2'}
    response = requests.post(url, data=payload)
    for user in response.json()[1:]:
        driver = FBDriver(user['profile_dir'], user['profilename'], logger)
        logger.info(f"User profile now: {user['profilename']}")
        # Visit home page, don't scroll
        hp = driver.visit_home(False)
        # Go to profile pages
        yp = driver.visit_your_pages()
        page_links = yp.page_links
        for i, page_link in enumerate(page_links):
            if i == 2:
                break
            # Visit news feed of the current page
            driver.browser.visit(page_link + "news_feed")
            logger.info(f"On Page {page_link}news_feed")
            PAGES_COUNT += 1
            logger.info(f"Visited pages count: {PAGES_COUNT}")
            sleep(10)
            #     Get all publications on the page
            publications_div = driver.browser.find_by_xpath('//div[@class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')
            logger.error(f"Publicaiton div on page: {len(publications_div)}")
            for pd in publications_div:
                try:
                    # hover on this to get the href populated
                    yp.hover(pd.find_by_xpath(
                        './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]'))
                    # Match the url of the pub to like
                    pub_link = pd.find_by_xpath(
                        './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')[
                        'href']
                    print(pub_link)
                    try:
                        pub_id = parse_qs(urlparse(pub_link).query)['story_fbid'][0]
                    except KeyError:
                        pub_id = urlparse(pub_link).path.split('/')[-1]
                    print(f"This pub id: {pub_id}")
                    if pub_id in posts_to_like:
                        sleep(5)
                        print("Matched this url to the api call")
                        # like the publications
                        pd.find_by_xpath(
                            './/div[@class="rq0escxv l9j0dhe7 du4w35lb j83agx80 cbu4d94t g5gj957u d2edcug0 hpfvmrgz rj1gh0hx buofh1pr n8tt0mok hyh9befq iuny7tx3 ipjc6fyt"]').click()
                except ElementDoesNotExist:
                    # Ignore element not exists exception as some pub divs are not pubs but some promoted content
                    pass
                finally:
                    sleep(5)
        driver.quit()
