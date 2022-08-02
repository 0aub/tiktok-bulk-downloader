# =================================
# ======= import libraries ========
# =================================

from base64 import b64decode, b64encode
from urllib.parse import parse_qsl, urlencode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
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

# =================================
# =========== arguments ===========
# =================================

parser = argparse.ArgumentParser()
parser.add_argument("-u",'--username', help='target username', type=str)
parser.add_argument("-g","--generate", help="generate json data (default: False)", default=False, action="store_true")
parser.add_argument("-d","--download", help="download saved posts (default: False)", default=False, action="store_true")
parser.add_argument("-nw","--no-watermark", help="download video with watermark (default: False)", default=False, action="store_true")
args = parser.parse_args()

if args.no_watermark:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException
    from webdriver_manager.chrome import ChromeDriverManager
    from subprocess import CREATE_NO_WINDOW

# =================================
# ========== parameters ===========
# =================================

# to calculate the number of the sent requests per run
REQUESTS_COUNTER = 0
# target username
USERNAME = args.username
# user page url
REFERRER = 'https://www.tiktok.com/@' + USERNAME
# static user agent
USER_AGENT = 'TikTok 16.0.16 rv:103005 (iPhone; iOS 11.1.4; en_EN) Cronet' # 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
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
    'browser_version': USER_AGENT,
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
# to be assigned later
USER_DETAILS = None

# =================================
# ======= params encryption =======
# =================================

# function to convert dictionery params to tiktok params
def encrypt(r, string=False):
    if not string:
      s = urlencode(r, doseq=True, quote_via=lambda s, *_: s)
    else:
      s = r
    key = "webapp1.0+202106".encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    ct_bytes = cipher.encrypt(pad(s.encode("utf-8"), AES.block_size))
    return b64encode(ct_bytes).decode("utf-8")

# function to convert tiktok params to dictionery params dictionery
def decrypt(s, string=False):
    key = "webapp1.0+202106".encode("utf-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    ct = b64decode(s)
    s = unpad(cipher.decrypt(ct), AES.block_size)
    decoded = s.decode("utf-8")
    if not string:
      return dict(parse_qsl(decoded, keep_blank_values=True))
    return decoded

# function to convert url params to dictionery (helped me to create the proper headers and params)
def urldncoder(params_string):
    # create empty dictionery
    params = dict()
    # get the parameter by splitting the string with "&"
    # split the parameter with "=" to get the dictionery key and value
    [params.update({ param.split('=')[0] : param.split('=')[1] }) for param in params_string.split('&')]
    # return params dictionery
    return params

# =================================
# ====== main communications ======
# =================================

# function to send a proper request to tiktok hidden apis
def tiktok_request(path, x_tt_params=None):
    # concat api endpoint with the base url
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
                "user-agent": USER_AGENT,
                "x-secsdk-csrf-token": None,
                "x-tt-params": x_tt_params,
            }
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # return tiktok api response as json
    return json.loads(requests.get(url, headers=headers).text)

# function to get and assign secret user id
def update_user():
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # add username and token to user detail api
    path = '/api/user/detail/?uniqueId={}&msToken={}'.format(USERNAME, PARAMS['msToken'])
    # catch if the user input was invalid
    try:
        # update secret user id in params dictionary with the extracted secUid from user detail api
        response = tiktok_request(path, x_tt_params=None)
        PARAMS['secUid'] = response['userInfo']['user']['secUid']
        # assign global user details object
        global USER_DETAILS
        USER_DETAILS = response['userInfo']
    except:
        raise Exception(f'''
        We could not find data about {USERNAME}.
        Take a look to these tips and try again.
          - Do not add @ in the beginning of the username
          - This script does not accept private accounts yet
        ''')

# function to get all user posts ids
def get_posts():
    # assign secret user id
    update_user()
    # loop appends collected posts data until "hasMore" attribute become False
    data = []
    while True:
        # encrypt params dictionery to convert it to tiktok params
        x_tt_params = encrypt(PARAMS)
        # add token to posts api
        path = '/api/post/item_list?msToken={}'.format(PARAMS['msToken'])
        # send a request to tiktok api
        current_data = tiktok_request(path, x_tt_params)
        # update cursor number to get the next ids
        PARAMS['cursor'] = current_data['cursor']
        if current_data['cursor'] == '0':
            continue
        # append the extracted data
        [data.append(item) for item in current_data['itemList']]
        # break the loop if "hasMore" attribute is False (the user out of posts)
        if not current_data['hasMore']:
            break
        # sleep for 300ms to prevent api block
        time.sleep(0.3)
    # return videos ids
    return data

# =================================
# ======== data generation ========
# =================================

# function to generate json file that contains all user posts data
def generate_data():
    print('[INFO]:  Generating json data...')
    # assign global user details and get posts data
    messy_posts = get_posts() 
    # loop over responses list
    posts = []
    for post in tqdm(messy_posts, desc='[INFO]:  Gathering posts: '):
        # assign posts data
        posts.append({
            'id': post['video']['id'],
            'date': datetime.fromtimestamp(post['createTime']),
            'description': post,
            'comments': post['stats']['commentCount'],
            'likes': post['stats']['diggCount'],
            'play': post['stats']['playCount'],
            'share': post['stats']['shareCount'],            
            'music': post['music']['playUrl'],
            'video': post['video']['playAddr'],
            'duration': post['video']['duration'],
            'ratio': post['video']['ratio'],
        })
    # assign user data
    user_data = {
        'id': USER_DETAILS['user']['id'],
        'avatar' : USER_DETAILS['user']['avatarLarger'],
        'nickname': USER_DETAILS['user']['nickname'],
        'username': USER_DETAILS['user']['uniqueId'],
        'secret_uid' : USER_DETAILS['user']['secUid'],
        'follower' : USER_DETAILS['stats']['followerCount'],
        'following' : USER_DETAILS['stats']['followingCount'],
        'likes': USER_DETAILS['stats']['heartCount'],
        'videos': USER_DETAILS['stats']['videoCount'],
        'isUnderAge18': USER_DETAILS['user']['isUnderAge18'],
        'verified': USER_DETAILS['user']['verified'],
        'posts': sorted(posts, key=lambda post: post['id'])
    }
    # generate json file name
    file_name = USERNAME + datetime.now().strftime("-%b_%d_%Y_%H-%M-%S.json")
    # save json file
    with open(file_name, 'w') as f:
        f.write(json.dumps(user_data, default=str))
    print('[INFO]:  Saved as ', file_name)

# =================================
# ========= no watermark ==========
# =================================

# set no watermark step environment
def nw_setup():
    # hide chrome driver window
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    # create chrome service with hiding flags
    service = Service(ChromeDriverManager().install())
    service.creationflags = CREATE_NO_WINDOW
    # return running chrome driver
    return webdriver.Chrome(service=service, options=options)

# get random site data from encrypted sites
def random_site():
    sites = 'eyw66467is0yHBmVtaYRoLqLYQ40ydyyGCaNhdsHkVHUjX2KN2r22G4/Bylm34eN4\
    HaTOjbAfShkw1Rkma0md6USAoINztZSZ1lhGkzAxQ8ah75ZVxADogL/MWNiOu6QCiMlEzXMIaQ\
    ptmWTDisa+GbWh6LaLfM+sN/cjtTm2Kr4jepPpNi9f4cT9/pSwclRxFyGj2CodWp7CH8Fvrw1l\
    6bgnEg+WYk27tT8dQ8GKvX3pte5Syow4soIEw8GNYpSHwSyEZ0r8RRuKfz5jGRoH9TWQLvSLAF\
    H9PKVkcPpP8qVvzsiJXU7ZGY6xho8IBET45g81Ix9lrseq/G9ATU4eExnYiU21L5VutUqrF+Z6\
    vUTCp/g/dUmzX+POncCEFwm6zR4C6tzdu1cWQ1c1k58UaqKd4zpwIRpHVJYAGzIgt37kQ+heXU\
    eGaTittU68FN0db6x09Dc7PJYQsWjlTq8G2OjGcQ6fu8D3LtCqS42+dlWzVGEqzvHy1k+4c/I8\
    S81r9zkIWLlfmIqGL9gvZyq13wUCOlvEXQ9eiAV2Qj/rxwjlBMZJiAsMpe2BSDLleqBo9dydb/\
    Gn+8j/d8AilAZL8k+xPkIwVPwCF7Pl11cw5a5XBdIxLXv5HeTfZOq9pVZasju4y1O8ciiat5xx\
    jIKQcvSl835rTpDX82l9vfEuxkbeWm0RkC70ZiSSofdGsUq9TyFn4HK3+uVfACkN+utLxpg0qY\
    M8hBBTknoon21oQxBeh0CQ72YrzfIyg27qrDDB+gtPlICOP8z5Qz18AIAq1HY8J2hYSiAl8XwY\
    tWzJJrdEFVEH8ijxIaoDNY4Dre2UA+6KN6BmRvPhPILm9lIUwk3I1alvTciHtwySHOm+gAS6qU\
    ZKm4VSAueWvpsTLzR2fV7FR00mpi9yyIJViyT3Mx3zi8T4x60BChvRyzLkJlnDrVDKHQOufaIi\
    awxiYv6701v+qOmEe5HNntfnmT2UieaTGiEYNVU3NfWxjG6zhzxz6ObFCi7rocGgZ5WqTcVjR1\
    B5uTc9tlY8L1yb542G6gh/gANKYTfQky4xId6Ajd074T1p5T4wsV0KHvhr4+eSKpZ9CVFr47cy\
    u8C/ALTAAIL1ztz5PjYeHkmXdb70fh9FmgOz/fLq6+AVFLHSxeDyFNy6lvhxetsLLoHBu+KfAE\
    jM7/asF2eXUEK4JWOZh1F4sdAj0JcbGBM9TRFPw7S'
    return random.choice(json.loads(decrypt(sites, string=True)))
    
# function to download any video with specific name
def nw_download(driver, id):
    errors = []
    while True:
        try:
            # increase requests counter by 1
            global REQUESTS_COUNTER
            REQUESTS_COUNTER += 1
            # random site data
            site = random_site()
            # sample -> https://www.tiktok.com/@valeriacarruyo/video/7124403717553556741
            video = f'https://www.tiktok.com/@{USERNAME}/video/{id}'
            # send request
            driver.get(site['url'])
            # get download url
            input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, site['input'])))
            input.send_keys(video)
            # submit
            submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, site['submit'])))
            submit.click()
            # get output element
            output = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, site['output'])))
            # extract videos urls from output element
            links = [item.get_attribute('href') for item in output.find_elements('xpath', '//a') if site['match'] in str(item.get_attribute('href'))]
            # extract and return NW url
            link = links[1 if 'ttsave' not in site['url'] else 0]
            # increase requests counter by 1
            REQUESTS_COUNTER += 1
            # create response object
            response = requests.get(link, stream=True)
            # specify file path
            file_name = id
            file_path = os.path.join(USERNAME, file_name + '.mp4')
            # create downloads directory with the target username
            if not os.path.exists(USERNAME):
                os.mkdir(USERNAME)    
            # download started
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            # check for downloading completeness
            if is_same_size(response, file_path):
                break
        except (TimeoutException, Exception) as e:
            errors.append({
                'time': datetime.now().strftime('%b_%d_%Y_%H-%M-%S'),
                'site': site['url'],
                'video': video,
                'error': str(e.__class__)
            })
            # error log
            log_file = 'errors_log'
            with open(log_file, '+w') as json_file:
                json.dump(errors, json_file)

# =================================
# =========== download ============
# =================================

# check if the file completely downloaded before
def is_same_size(response, file_path):
    if os.path.exists(file_path):
        return os.stat(file_path).st_size > 5000
    return False

# function to download any video with specific name
def download(link, file_name):
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # create response object
    response = requests.get(link, stream=True)
    # specify file path
    file_path = os.path.join(USERNAME, file_name + '.mp4')
    # create downloads directory with the target username
    if not os.path.exists(USERNAME):
        os.mkdir(USERNAME)    
    # download started
    with open(file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
        
# get last downloaded file
def is_downloaded(id):
    if not os.path.exists(USERNAME):
        return False
    return max(os.listdir(USERNAME)).split('.')[0] >= id

# function to download all posts list
def download_posts(posts, no_watermark=False):
    if no_watermark:
        driver = nw_setup()
        print('[WARN]:  No watermark download will take longer time...')
    # loop over all posts and download every post with its id as its name
    for post in tqdm(posts, desc='[INFO]:  Downloading posts: '):
        # check where the downloading stopped last time
        if not is_downloaded(post['id']):
            if not no_watermark:
                # download the stored video url
                download(post['video'], post['id'])
            else:
                # download from external sites
                nw_download(driver, post['id'])
    if no_watermark:
        driver.quit()
    print('\n[INFO]:  DONE')

# =================================
# ============= main ==============
# =================================

# main function
def main(args):
    # check if the script ran properly on not
    if not args.generate and not args.download:
        print('please run the script properly. for more info: https://github.com/0aub/tiktok-bulk-downloader')
        return 0
    # start timer
    start_time = time.time()
    # generate json data file
    if args.generate:
        generate_data()
    # download saved posts
    if args.download:
        # get latest saved file
        files = [file_name for file_name in os.listdir('./') if file_name.endswith('.json') and file_name.startswith(USERNAME)]
        files.sort(key=lambda x: os.path.getmtime(x))
        newest_file = files[-1]
        # read json file
        with open(newest_file, 'r') as json_file:
            json_data = json.load(json_file)
        download_posts(json_data['posts'], args.no_watermark)
    # print total number of requests and execution time
    print('[INFO]:  Number of sent requests: ', REQUESTS_COUNTER)
    print('[INFO]:  Execution time: ', str(time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))))

if __name__ == '__main__':
    main(args)