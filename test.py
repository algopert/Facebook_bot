# encoding: utf-8

import urllib
from urllib.parse import urlparse
import re

# url = 'https://www.facebook.com/Odds-Finder-is-a-SCAM-113218404722506'
url = 'https://www.facebook.com/profile.php?id=100083405164992'
# print(urlparse(url))
# print(urlparse(url).query)

print(int(re.search(r'\d+', url).group()))
if 'blocked_uid' in urlparse(url).query:
    print('ok')