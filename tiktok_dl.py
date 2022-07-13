# import libraries
from base64 import b64decode, b64encode
from urllib.parse import parse_qsl, urlencode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from fake_useragent import UserAgent
from tqdm import tqdm
from datetime import datetime
import argparse
import requests
import random
import json
import os
import string
import sys
import time

# cli arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u",'--username', help='target username', type=str)
parser.add_argument("-g","--generate", help="generate json data (default: False)", default=False, action="store_true")
parser.add_argument("-d","--download", help="download saved posts (default: False)", default=False, action="store_true")
parser.add_argument("-w","--watermark", help="download video with watermark (default: False)", default=False, action="store_true")
args = parser.parse_args()

# to calculate the number of the sent requests per run
REQUESTS_COUNTER = 0
# generate fake user agent
USER_AGENT = UserAgent()
# target username
USERNAME = str(args.username)
# user page url
REFERRER = 'https://www.tiktok.com/@' + USERNAME
# public parameters for api requests
PARAMS = {
    'X-Bogus': 'DFSzswVL0tGANHclS1bj8uF33wAr',
    '_signature': '_02B4Z6wo000018WkpgAAAIDDnJowbmNvu5vFpKKAAJOt67',
    'aid': '1988',
    'app_language': 'en',
    'app_name': 'tiktok_web',
    'battery_info': '1',
    'browser_language': 'en-US',
    'browser_name': 'Mozilla',
    'browser_online': 'true',
    'browser_platform': 'Win32',
    'browser_version': "5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    'channel': 'tiktok_web',
    'cookie_enabled': 'true',
    'count': '30',
    'cursor': 0,
    'device_id': "".join(random.choice(string.digits) for num in range(19)),
    'device_platform': 'web_pc',
    'focus_state': 'true',
    'from_page': 'user',
    'history_len': '11',
    'is_encryption': '1',
    'is_fullscreen': 'false',
    'is_page_visible': 'true',
    'language': 'en',
    'msToken': 'Yfl8tAwMq1EOio0kwE-wYVuVnUgFj-P0ogVJSJlsw3AOV3e_z_ZC6zioEMD1-dz3iXUB9yWBt5O3cleIp5vBWOcMOwga1P2py0-TwNtN4OTR29K9Jt0Y3v-32FGKqvcMlMtLxacobg0xlZHUQQ==',
    'os': 'windows',
    'priority_region': '',
    'referer': '',
    'region': 'SA',
    'root_referer': 'undefined',
    'screen_height': '1080',
    'screen_width': '1920',
    'secUid': '',
    'tz_name': 'Asia/Riyadh',
    'userId': 'undefined',
    'verifyFp': 'verify_khr3jabg_V7ucdslq_Vrw9_4KPb_AJ1b_Ks706M8zIJTq',
    'webcast_language': 'en'
}

# function to convert dictionery params to tiktok params
def encrypt(r):
    s = urlencode(r, doseq=True, quote_via=lambda s, *_: s)
    key = "webapp1.0+202106".encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    ct_bytes = cipher.encrypt(pad(s.encode("utf-8"), AES.block_size))
    return b64encode(ct_bytes).decode("utf-8")

# function to convert tiktok params to dictionery params dictionery
def decrypt(s):
    key = "webapp1.0+202106".encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    ct = b64decode(s)
    s = unpad(cipher.decrypt(ct), AES.block_size)
    return dict(parse_qsl(s.decode("utf-8"), keep_blank_values=True))

# function to convert url params to dictionery (helped me to create the proper headers and params)
def urldncoder(params_string):
    # create empty dictionery
    params = dict()
    # get the parameter by splitting the string with "&"
    # split the parameter with "=" to get the dictionery key and value
    [params.update({ param.split('=')[0] : param.split('=')[1] }) for param in params_string.split('&')]
    # return params dictionery
    return params

# function to send a proper request to tiktok hidden apis
def tiktok_request(path, x_tt_params=None):
    # concate api endpoint with the base url
    url = "https://tiktok.com" + path
    # create the requests headers for tiktok api request
    headers = {
                "authority": "m.tiktok.com",
                "method": "GET",
                "path": path,
                "scheme": "https",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip",
                "accept-language": "en-US,en;q=0.9",
                "origin": REFERRER,
                "referer": REFERRER,
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "none",
                "sec-gpc": "1",
                "user-agent": "5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
                "x-secsdk-csrf-token": None,
                "x-tt-params": x_tt_params,
            }
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # return tiktok api response as json
    return json.loads(requests.get(url, headers=headers).text)

# function to get and assign secret user id
def update_uid():
    # add username and token to user detail api
    path = '/api/user/detail/?uniqueId={}&msToken={}'.format(USERNAME, PARAMS['msToken'])
    # update secret user id in params dictionery with the extracted secUid from user detail api
    PARAMS['secUid'] = tiktok_request(path, x_tt_params=None)['userInfo']['user']['secUid']

# function to get all user posts ids
def get_ids():
    # assign secret user id
    update_uid()
    # loop appends collected ids until "hasMore" arrtibute become False
    ids = []
    while True:
        # encrypt params dictionery to convert it to tiktok params
        x_tt_params = encrypt(PARAMS)
        # add token to posts api
        path = '/api/post/item_list?msToken={}'.format(PARAMS['msToken'])
        # send a request to tiktok api
        data = tiktok_request(path, x_tt_params)
        # update cursor number to get the next ids
        PARAMS['cursor'] = data['cursor']
        # extract videos ids from tiktok response
        current_ids = [vid['id'] for vid in data['itemList']]
        # append the extracted ids
        ids = list(set(ids + current_ids))
        # break the loop if "hasMore" arrtibute is False (the user out of posts)
        if not data['hasMore']:
            break
        # sleep for 300ms to prevent api block
        time.sleep(0.3)
    # return videos ids
    return ids

# function to prepare requests urls of every video id
def get_vid_api_requests():
    return ['https://toolav.herokuapp.com/id/?video_id=' + id for id in get_ids()]

# function to send requests with 300ms sleep
def slow_request(url):
    # sleep for 300ms
    time.sleep(0.3)
    # generate random user agent
    headers={'User-Agent': USER_AGENT.random}
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # return the response as json
    return json.loads(requests.get(url, headers=headers).text)

# function to get videos data from api responses
# it will return a list of api responses for every gathered video id
def get_vid_api_responses():
    # get video api requests
    # urls is list of urls that is prepared to be sent as api requests
    urls = get_vid_api_requests()
    # return responses slowly (with sleep) to prevent some errors
    return [slow_request(url) for url in tqdm(urls, desc='gathering posts data: ')]

# function to generate json file that contains all user posts data
def generate_data():
    # get videos data from api responses
    # responses is a list of api responses for every gathered video id
    responses = get_vid_api_responses()
    # assign user data
    first_item = responses[0]['item']['author']
    user_data = {
        'avatar' : first_item['avatarLarger'],
        'nickname': first_item['nickname'],
        'username': first_item['uniqueId'],
        'secret_uid' : first_item['secUid'],
        'posts': []
    }
    # loop over responses list
    for item in tqdm(responses, desc='organizing user data: '):
        # assign posts data
        user_data['posts'].append({
            'id': item['item']['id'],
            'description': item['item']['desc'],
            'comments': item['item']['stats']['commentCount'],
            'likes': item['item']['stats']['diggCount'],
            'play': item['item']['stats']['playCount'],
            'share': item['item']['stats']['shareCount'],
            'with_watermark': item['item']['video']['downloadAddr'],
            'without_watermark': item['item']['video']['playAddr'],
            'duration': item['item']['video']['duration'],
            'ratio': item['item']['video']['ratio'],
        })
    # generate json file name
    file_name = USERNAME + datetime.now().strftime("-%b_%d_%Y_%H-%M-%S.json")
    # save json file
    with open(file_name, 'w') as file:
        file.write(json.dumps(user_data, indent = 4))
    print('saved as ', file_name)

# function to download any video with specific name
def download(link, file_name, dir):
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # create response object
    response = requests.get(link, stream=True)
    # specify file path
    file_path = os.path.join(dir, file_name + '.mp4')
    # create downloads directory with the target username
    if not os.path.exists(dir):
        os.mkdir(dir)
    # download started
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)

# function to download all posts list
def download_posts(posts, watermark, dir):
    # specify watermark option
    option = 'with_watermark' if watermark else 'without_watermark'
    # loop over all posts and download every post with its id as its name
    for post in tqdm(posts, desc='downloading posts: '):
        download(post[option][0], post['id'], dir)
    print('\nDONE')

# main function
def main(args):
    # generate json data file
    if args.generate:
        generate_data()
    # download saved posts
    if args.download:
        # get latest saved file
        files = [file_name for file_name in os.listdir('./') if file_name.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(x))
        newest_file = files[-1]
        # read json file
        with open(newest_file, 'r') as json_file:
            json_data = json.load(json_file)
        download_posts(json_data['posts'], args.watermark, json_data['username'])
    # print total number of requests
    print('number of sent requests: ', REQUESTS_COUNTER)

if __name__ == '__main__':
    main(args)