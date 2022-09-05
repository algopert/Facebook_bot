import getpass as gp
import json
import os
import socket

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# System settings
WINDOWS_USER = gp.getuser()
# Add _2 to local ip if the username endswith 2
# Try to connect to the API server to get public facing IP address
# Else get local IP using system commands

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("http://example.com/", 1))  # connect() for UDP doesn't send packets
    LOCAL_IP = s.getsockname()[0]
    s.close()
    print('Found IP using API server connection')
except:
    LOCAL_IP = socket.gethostbyname(socket.gethostname())
    print('Found IP using hostname method')
finally:
    # Add _2 if required
    LOCAL_IP = f"{LOCAL_IP}{'_2' if WINDOWS_USER.endswith('2') else ''}"
    print(f"LOCAL_IP: {LOCAL_IP}")

# The config file is expected to be at the root of the project folder
configuration_data = json.load(open(os.path.join(PROJECT_ROOT, 'config.json')))

COMMENT_HOST = configuration_data['comment_host']
REACT_HOST = configuration_data['react_host']
MODERATE_HOST = configuration_data['moderate_host']
LOG_PATH = configuration_data['log_path']
SCREENSHOTS_PATH = configuration_data['screenshots_path']

# Sharing publications settings
REACTION_LIMIT_HIGH = 10
REACTION_LIMIT_LOW = 5
MAX_PAGE_VISIT = 6
MAX_PUB_SCAN = 10

# Mailer settings, hopefully it's same for all scripts
MAIL_SERVER = configuration_data['smtp_server']
MAIL_PORT = configuration_data['smtp_port']
MAIL_PROTOCOL = configuration_data['smtp_protocol']
MAIL_USER = configuration_data['smtp_user']
MAIL_PASSWORD = configuration_data['smtp_password']
MAIL_FROM = configuration_data['mail_from']
MAIL_TO = configuration_data['mail_to']

# timeout in seconds for moderation of single publication
MODERATION_TIMEOUT = 60 * 5
# New config file structure for the merged settings
# {
#     "comment_host": "http://comment.com",
#     "react_host": "http://likes.com",
#     "moderate_host": "htttp://moderate.com",
#     "log_path": "absolute directory path for logs",
#     "screenshots_path": "absolute directory path for screenshots",
#     "smtp_server": "",
#     "smtp_port": "",
#     "smtp_protocol": "",
#     "smtp_user": "",
#     "smtp_password": "",
#     "mail_from": "",
#     "mail_to": ""
# }


# Make the directory for screenshots and logs if not available
for p in (SCREENSHOTS_PATH, LOG_PATH):
    try:
        # Allow absolute path or relative to project root for log and screenshots
        os.mkdir(os.path.join(PROJECT_ROOT, p))
    except FileExistsError:
        pass
