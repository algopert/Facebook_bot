import socket
import traceback
import requests
from getpass import getuser

WINDOWS_USER = getuser()

API_URL = 'http://likes.botobot.xyz'
LIKE_URL = 'http://likes.botobot.xyz/api/disable_api_alerts'
MODERATION_URL = 'http://phpcomments.botobot.xyz/api/disable_moderation_api_alerts'
COMMENT_URL = 'http://phpcomments.botobot.xyz/api/disable_comments_api_alerts'


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((API_URL, 1))  # connect() for UDP doesn't send packets
        LOCAL_IP = s.getsockname()[0]
        s.close()
        print('Found IP using API server connection')
    except:
        LOCAL_IP = socket.gethostbyname(socket.gethostname())
        print('Found IP using hostname method')
    finally:
        # Add _2 if required
        LOCAL_IP = f"{LOCAL_IP}{'_2' if WINDOWS_USER.endswith('2') else ''}"
    return LOCAL_IP


def disable_alerts(ip):
    data = {'server_ip': ip}
    print('Disabling Like alerts')
    try:
        response = requests.post(LIKE_URL, data=data)
        print(response.status_code, response.text)
    except Exception:
        traceback.print_exc()

    print('Disabling Comment alerts')
    try:
        response = requests.post(COMMENT_URL, data=data)
        print(response.status_code, response.text)
    except Exception:
        traceback.print_exc()

    print('Disabling Moderation alerts')
    try:
        response = requests.post(MODERATION_URL, data=data)
        print(response.status_code, response.text)
    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    local_ip = get_ip()
    disable_alerts(local_ip)
