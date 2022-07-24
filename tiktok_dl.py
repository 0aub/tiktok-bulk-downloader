# =================================
# ======= import libraries ========
# =================================

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

# =================================
# =========== arguments ===========
# =================================

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="target username", type=str)
parser.add_argument(
    "-g",
    "--generate",
    help="generate json data (default: False)",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-d",
    "--download",
    help="download saved posts (default: False)",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-nw",
    "--no-watermark",
    help="download video with watermark (default: False)",
    default=False,
    action="store_true",
)
args = parser.parse_args()

if args.no_watermark:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

# =================================
# ========== parameters ===========
# =================================

# to calculate the number of the sent requests per run
REQUESTS_COUNTER = 0
# target username
USERNAME = args.username
# user page url
REFERRER = "https://www.tiktok.com/@" + USERNAME
# static user agent
USER_AGENT = "TikTok 16.0.16 rv:103005 (iPhone; iOS 11.1.4; en_EN) Cronet"  # 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
# public parameters for api requests
PARAMS = {
    "X-Bogus": "DFSzswVL0tGANHclS1bj8uF33wAr",
    "_signature": "_02B4Z6wo000018WkpgAAAIDDnJowbmNvu5vFpKKAAJOt67",
    "aid": "1988",
    "app_language": "en",
    "app_name": "tiktok_web",
    "battery_info": "1",
    "browser_language": "en-US",
    "browser_name": "Mozilla",
    "browser_online": "true",
    "browser_platform": "Win32",
    "browser_version": USER_AGENT,
    "channel": "tiktok_web",
    "cookie_enabled": "true",
    "count": "30",
    "cursor": 0,
    "device_id": "".join(random.choice(string.digits) for num in range(19)),
    "device_platform": "web_pc",
    "focus_state": "true",
    "from_page": "user",
    "history_len": "11",
    "is_encryption": "1",
    "is_fullscreen": "false",
    "is_page_visible": "true",
    "language": "en",
    "msToken": "Yfl8tAwMq1EOio0kwE-wYVuVnUgFj-P0ogVJSJlsw3AOV3e_z_ZC6zioEMD1-dz3iXUB9yWBt5O3cleIp5vBWOcMOwga1P2py0-TwNtN4OTR29K9Jt0Y3v-32FGKqvcMlMtLxacobg0xlZHUQQ==",
    "os": "windows",
    "priority_region": "",
    "referer": "",
    "region": "SA",
    "root_referer": "undefined",
    "screen_height": "1080",
    "screen_width": "1920",
    "secUid": "",
    "tz_name": "Asia/Riyadh",
    "userId": "undefined",
    "verifyFp": "verify_khr3jabg_V7ucdslq_Vrw9_4KPb_AJ1b_Ks706M8zIJTq",
    "webcast_language": "en",
}
# to be assined later
USER_DETAILS = None

# =================================
# ======= params encryption =======
# =================================

# function to convert dictionery params to tiktok params
def encrypt(r, txt=False):
    if not txt:
        s = urlencode(r, doseq=True, quote_via=lambda s, *_: s)
    else:
        s = r
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
    [
        params.update({param.split("=")[0]: param.split("=")[1]})
        for param in params_string.split("&")
    ]
    # return params dictionery
    return params


# =================================
# ====== main communications ======
# =================================

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
    path = "/api/user/detail/?uniqueId={}&msToken={}".format(
        USERNAME, PARAMS["msToken"]
    )
    # catch if the user input was invalid
    try:
        # update secret user id in params dictionery with the extracted secUid from user detail api
        response = tiktok_request(path, x_tt_params=None)
        PARAMS["secUid"] = response["userInfo"]["user"]["secUid"]
        # assign global user details object
        global USER_DETAILS
        USER_DETAILS = response["userInfo"]
    except:
        raise Exception(
            f"""
        We could not find data about {USERNAME}.
        Take a look to these tips and try again.
          - Do not add @ in the beginning of the username
          - This script does not accept private accounts yet
        """
        )


# function to get all user posts ids
def get_posts():
    # assign secret user id
    update_user()
    # loop appends collected posts data until "hasMore" arrtibute become False
    data = []
    while True:
        # encrypt params dictionery to convert it to tiktok params
        x_tt_params = encrypt(PARAMS)
        # add token to posts api
        path = "/api/post/item_list?msToken={}".format(PARAMS["msToken"])
        # send a request to tiktok api
        current_data = tiktok_request(path, x_tt_params)
        # update cursor number to get the next ids
        PARAMS["cursor"] = current_data["cursor"]
        if current_data["cursor"] == "0":
            continue
        # append the extracted data
        [data.append(item) for item in current_data["itemList"]]
        # break the loop if "hasMore" arrtibute is False (the user out of posts)
        if not current_data["hasMore"]:
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
    print("[INFO]:  Generating json data...")
    # assign global user details and get posts data
    posts = get_posts()
    # assign user data
    user_data = {
        "id": USER_DETAILS["user"]["id"],
        "avatar": USER_DETAILS["user"]["avatarLarger"],
        "nickname": USER_DETAILS["user"]["nickname"],
        "username": USER_DETAILS["user"]["uniqueId"],
        "secret_uid": USER_DETAILS["user"]["secUid"],
        "follower": USER_DETAILS["stats"]["followerCount"],
        "following": USER_DETAILS["stats"]["followingCount"],
        "likes": USER_DETAILS["stats"]["heartCount"],
        "videos": USER_DETAILS["stats"]["videoCount"],
        "isUnderAge18": USER_DETAILS["user"]["isUnderAge18"],
        "verified": USER_DETAILS["user"]["verified"],
        "posts": [],
    }
    # loop over responses list
    for post in tqdm(posts, desc="[INFO]:  Gathering posts: "):
        # assign posts data
        user_data["posts"].append(
            {
                "id": post["video"]["id"],
                "date": datetime.fromtimestamp(post["createTime"]),
                "description": post,
                "comments": post["stats"]["commentCount"],
                "likes": post["stats"]["diggCount"],
                "play": post["stats"]["playCount"],
                "share": post["stats"]["shareCount"],
                "music": post["music"]["playUrl"],
                "video": post["video"]["playAddr"],
                "duration": post["video"]["duration"],
                "ratio": post["video"]["ratio"],
            }
        )
    # generate json file name
    file_name = USERNAME + datetime.now().strftime("-%b_%d_%Y_%H-%M-%S.json")
    # save json file
    with open(file_name, "w") as f:
        f.write(json.dumps(user_data, default=str))
    print("[INFO]:  Saved as ", file_name)


# =================================
# ========= no watermark ==========
# =================================

# set no watermark step environment
def nw_setup():
    # run phantom driver
    driver = webdriver.PhantomJS("phantomjs")
    string = "f3y2s2FPdjLfAS4FWe2+iHpQycxKVPovLc63GXBdG15WqdRtSUXvnK9CUjnrULSspRsdCCXM/LxR+UjmQ4znIsHoyYTsW3m4Krj4obW3u00="
    return (driver, string)


# get post url withour watermark
def nw_url(driver, base_url, id):
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # send request
    request = (
        "=".join([str(item) for item in list(decrypt(base_url).items())[0]])
        .replace("param", "{}")
        .format(USERNAME, id)
    )
    driver.get(request)
    # get download url
    downloads = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="download"]'))
    )
    return [
        item.get_attribute("href") for item in downloads.find_elements("xpath", ".//a")
    ][0]


# =================================
# =========== download ============
# =================================

# function to download any video with specific name
def download(link, file_name):
    # increase requests counter by 1
    global REQUESTS_COUNTER
    REQUESTS_COUNTER += 1
    # create response object
    response = requests.get(link, stream=True)
    # specify file path
    file_path = os.path.join(USERNAME, file_name + ".mp4")
    # create downloads directory with the target username
    if not os.path.exists(USERNAME):
        os.mkdir(USERNAME)
    # download started
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


# function to download all posts list
def download_posts(posts, no_watermark=False):
    if no_watermark:
        (driver, base_url) = nw_setup()
        print("[WARN]:  No watermark download will take longer time...")
    # loop over all posts and download every post with its id as its name
    for post in tqdm(posts, desc="[INFO]:  Downloading posts: "):
        download(
            nw_url(driver, base_url, post["id"]) if no_watermark else post["video"],
            post["id"],
        )
    print("\n[INFO]:  DONE")


# =================================
# ============= main ==============
# =================================

# main function
def main(args):
    # generate json data file
    if args.generate:
        generate_data()
    # download saved posts
    if args.download:
        # get latest saved file
        files = [
            file_name for file_name in os.listdir("./") if file_name.endswith(".json")
        ]
        files.sort(key=lambda x: os.path.getmtime(x))
        newest_file = files[-1]
        # read json file
        with open(newest_file, "r") as json_file:
            json_data = json.load(json_file)
        download_posts(json_data["posts"], args.no_watermark)
    # print total number of requests
    print("[INFO]:  Number of sent requests: ", REQUESTS_COUNTER)


if __name__ == "__main__":
    main(args)
