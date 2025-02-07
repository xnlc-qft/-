# File    : main.py
# Email   : amu155@outlook.com
# Author  : amu155
# Soft    : PyCharm
import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import re
import execjs
import ddddocr


class CX:
    def __init__(self):
        # 在此处输入手机号
        self.phonenum = ''
        self.route = '5f97531a710da073c78ad237716af1bf'
        self.fid = '464'
        self.ua = UserAgent()
        self.captchaId = 'GcXX5vewqE7DezKGlyvleKCnkTglvGpL'
        self.callback = 'cx_captcha_function'
        self.timestamp = time.time()
        self.JSESSIONID = 'BAD10012C6EC93DA72D1892940A77AD6'
        self.spaceFidEnc = '83BAC592D6472F8F9E115DD077B84999'
        self.jrose = 'D0CE12E3282CC916FEEE9E5736C8EA5F.ans'
        with open('main.js', 'r', encoding='utf-8') as file:
            self.js_code = file.read()
        self.context = execjs.compile(self.js_code)
        self.cookies = {
            'route': self.route,
            'fid': self.fid,
            'source': '""',
        }
        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'https://passport2.chaoxing.com/',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua.random,
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.cookies2 = {
            'route': self.route,
            'retainlogin': '1',
            'fid': self.fid,
            'source': '""',
            'JSESSIONID': self.JSESSIONID,
        }
        self.headers2 = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'https://passport2.chaoxing.com/login?loginType=2&newversion=true&fid=-1&hidecompletephone=0&ebook=0&allowSkip=0&forbidotherlogin=0&refer=https%3A%2F%2Fi.chaoxing.com&accounttip=&pwdtip=&quick=0&doubleFactorLogin=0&independentId=0&independentNameId=0&retainlogin=1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua.random,
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def get_return_timestamp(self):
        timestamp = int(self.timestamp * 1000)
        url = 'https://captcha.chaoxing.com/captcha/get/conf'
        params = {
            'callback': self.callback,
            'captchaId': self.captchaId,
            '_': str(timestamp),
        }
        response = requests.get(url=url, params=params, cookies=self.cookies, headers=self.headers)
        match = re.search(r'\((.*?)\)', response.text)
        raw_strdata = json.loads(match.group(1))
        return_timestamp = raw_strdata['t']
        return str(return_timestamp)

    def get_reverse_params(self, return_timestamp):
        result = self.context.call("get_params", return_timestamp)
        return result

    def get_slideimages(self, jsparams):
        url = 'https://captcha.chaoxing.com/captcha/get/verification/image'
        params = {
            'callback': self.callback,
            'captchaId': self.captchaId,
            'type': 'slide',
            'version': '1.1.20',
            'captchaKey': jsparams['captchaKey'],
            'token': jsparams['token'],
            'referer': 'https://passport2.chaoxing.com/login?loginType=2&newversion=true&fid=-1&hidecompletephone=0&ebook=0&allowSkip=0&forbidotherlogin=0&refer=https%3A%2F%2Fi.chaoxing.com&accounttip=&pwdtip=&quick=0&doubleFactorLogin=0&independentId=0&independentNameId=0&retainlogin=1',
            'iv': jsparams['iv'],
            '_': str((self.timestamp * 1000) + 1),
        }

        response = requests.get(
            url=url, params=params, cookies=self.cookies, headers=self.headers,
        )
        match = re.search(r'\((.*?)\)', response.text)
        return_image_url = json.loads(match.group(1))
        return return_image_url

    def get_image(self, url):
        response = requests.get(
            url=url,
            cookies=self.cookies,
            headers=self.headers,
        )
        return response.content

    def get_axis(self, images):
        big_img_url = images['imageVerificationVo']['shadeImage']
        small_img_url = images['imageVerificationVo']['cutoutImage']
        img_return_token = images['token']
        with ThreadPoolExecutor(max_workers=2) as executor:
            big_img, small_img = executor.map(cx.get_image, [big_img_url, small_img_url])
        det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
        axis = det.slide_match(big_img, small_img, simple_target=True)

        at = {
            'axis': axis['target'][0],
            'token': img_return_token
        }
        return at

    def pass_captchar(self, axis_token, jsparams):
        textClickArr = '[{"x":' + str(axis_token['axis']) + '}]'
        url = 'https://captcha.chaoxing.com/captcha/check/verification/result'
        params = {
            'callback': self.callback,
            'captchaId': self.captchaId,
            'type': 'slide',
            'token': axis_token['token'],
            'textClickArr': textClickArr,
            'coordinate': '[]',
            'runEnv': '10',
            'version': '1.1.20',
            't': 'a',
            'iv': jsparams['iv'],
            '_': str((self.timestamp * 1000) + 2),
        }
        response = requests.get(url=url, params=params, cookies=self.cookies, headers=self.headers)
        match = re.search(r'\((.*?)\)', response.text)
        raw_validate = json.loads(match.group(1))
        validate_str = raw_validate['extraData']
        validate_dict = json.loads(validate_str)
        return validate_dict['validate']

    def get_checksum(self, validate_dict):
        url = 'https://passport2.chaoxing.com/num/phonecode'
        params = {
            'phone': self.phonenum,
            'code': '',
            'type': '1',
            'needcode': 'false',
            'countrycode': '86',
            'validate': validate_dict,
            'fid': '-1',
        }
        response = requests.get(url=url, params=params, cookies=self.cookies2, headers=self.headers2)
        print(response.text)

    def input_checksum(self):
        raw_vercode = input(str("请输入短信验证码:"))
        vercode = self.context.call("get_encrypt_param", raw_vercode)
        url = 'https://passport2.chaoxing.com/fanyaloginbycode'
        data = {
            'fid': '-1',
            'uname': self.phonenum,
            'verCode': vercode,
            'refer': 'https%3A%2F%2Fi.chaoxing.com',
            'doubleFactorLogin': '0',
            'independentNameId': '0',
        }

        response = requests.post(url=url, cookies=self.cookies2, headers=self.headers2, data=data)
        json_cookies = {
            "DSSTASH_LOG": response.cookies['DSSTASH_LOG'],
            "UID": response.cookies['UID'],
            "_d": response.cookies['_d'],
            "_uid": response.cookies['_uid'],
            "chaoxinguser": response.cookies['chaoxinguser'],
            "cx_p_token": response.cookies['cx_p_token'],
            "p_auth_token": response.cookies['p_auth_token'],
            "uf": response.cookies['uf'],
            "uname": response.cookies['uname'],
            "vc2": response.cookies['vc2'],
            "vc3": response.cookies['vc3'],
            "xxtenc": response.cookies['xxtenc']
        }
        return json_cookies

    def pass_ver_302(self, json_cookies):
        url = 'https://i.chaoxing.com/'
        cookies = {
            'spaceFidEnc': self.spaceFidEnc,
            'jrose': self.jrose,
            'source': '""',
            'chaoxinguser': '1',
            'uname': '""',
            '_uid': json_cookies['_uid'],
            'uf': json_cookies['uf'],
            '_d': json_cookies['_d'],
            'UID': json_cookies['UID'],
            'vc2': json_cookies['vc2'],
            'vc3': json_cookies['vc3'],
            'cx_p_token': json_cookies['cx_p_token'],
            'p_auth_token': json_cookies['p_auth_token'],
            'xxtenc': json_cookies['xxtenc'],
            'DSSTASH_LOG': json_cookies['DSSTASH_LOG'],
        }
        requests.get(url=url, cookies=cookies, headers=self.headers)

    def mock_login(self, json_cookies):
        url = 'https://i.chaoxing.com/base'
        cookies = {
            'spaceFidEnc': self.spaceFidEnc,
            'jrose': self.jrose,
            'source': '""',
            'chaoxinguser': '1',
            'uname': '""',
            '_uid': json_cookies['_uid'],
            'uf': json_cookies['uf'],
            '_d': json_cookies['_d'],
            'UID': json_cookies['UID'],
            'vc2': json_cookies['vc2'],
            'vc3': json_cookies['vc3'],
            'cx_p_token': json_cookies['cx_p_token'],
            'p_auth_token': json_cookies['p_auth_token'],
            'xxtenc': json_cookies['xxtenc'],
            'DSSTASH_LOG': json_cookies['DSSTASH_LOG'],
        }
        params = {
            't': str(self.timestamp * 1000),
        }
        response = requests.get(url=url, params=params, cookies=cookies, headers=self.headers)
        print("登录状态:", response.status_code)


if __name__ == '__main__':
    cx = CX()
    return_timestamp = cx.get_return_timestamp()
    jsparams = cx.get_reverse_params(return_timestamp)
    images = cx.get_slideimages(jsparams)
    axis_token = cx.get_axis(images)
    validate_dict = cx.pass_captchar(axis_token, jsparams)
    cx.get_checksum(validate_dict)
    json_cookies = cx.input_checksum()
    cx.pass_ver_302(json_cookies)
    cx.mock_login(json_cookies)
