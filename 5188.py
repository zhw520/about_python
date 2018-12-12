# -*- coding: utf-8 -*-
import requests
from lxml import etree
from time import sleep
import base64
import sys
import urllib
import json

login_url = 'https://account.5118.com/account/LoginConfirm'
account = {"uname":"15001364950", "pwd":"13522500147"}

pwd_base64 = base64.b64encode(account['pwd'].encode('utf-8')).decode("utf-8")
login_data = {'uname':account['uname'],'pwd':pwd_base64, 'remember':'false', 'isKf5':'false'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' 'Chrome/51.0.2704.63 Safari/537.36'
}
cookies = "ASP.NET_SessionId=01ajw5guk3kkt3nk5p0jyr2c; Hm_lvt_f3b3086e3d9a7a0a65c711de523251a6=1543556013; PromoteCookie=; .AspNet.ApplicationCookie=71D1SjQQeXcD1mnA60ld6BXwdOUHVH3QiKWVyYs6kxJLInPddIgrO0z8BPimfA-Kbj4NjEYFEsIu5Ya1aFXgoC63z-4Jt9UrGO5efWmqChUOvsArpGeKFOTZQvw-iSTbOQfooydFPPnJWrd0nNJWfdn5RjtKnaaviVBK4JOND74MdTsgnnIsMCHlAyFjcIFle6CqtWQiHn55nJntk4TlfzsbhuTnHjRywGyFCEh5xnZyBvqdeDfhfGt9SyVdO2kRV_f719zKIfbVqi98ZQuppAPCCuvXGoaBFsY9WUhNa0H1ea0GWbKznnJU68mAX-rlCy5ShoswfqK2am09oBF5VHzmsImTDGucx1u3oMvVTvQabVSL-2yX9gtt27VTt2ZbBs-hO5xpa0bzzk3BprR_0HTl2RyX91Z3yxl7IJqQrng; Hm_lpvt_f3b3086e3d9a7a0a65c711de523251a6=1543822212"


def cookie_format(cookie_param):
    cookie = {}
    for line in cookie_param.split(';'):
        key, value = line.split('=', 1)
        cookie[key] = value
    return cookie

def get_cookie_by_login(login_url):
    session = requests.session()
    login_result = session.post(login_url, headers=headers, data=login_data)
    if json.loads(login_result.text)['status'] != 1:
        print('登录失败，请检查是否IP被bang或header头被禁用')
        exit()
    c = requests.cookies.RequestsCookieJar()
    c.set('cookie-name','cookie-value')
    session.cookies.update(c)
    return session.cookies.get_dict()

def get_html_by_ci(citiao):
    encodestr = base64.b64decode(citiao.encode('utf-8'))
    ci_urlencode = str(encodestr,'utf-8')

    cookie_dict = cookie_format(cookies)
    data = requests.get('https://www.5118.com/seo/newwords/' + ci_urlencode, headers=headers, cookies=cookie_dict)
    if data.status_code == 403:
        data = requests.get('https://www.5118.com/seo/newwords/' + ci_urlencode, headers=headers, cookies=get_cookie_by_login(login_url))
    elif data.status_code != 200 and data.status_code != 403:
        print("抓取数据失败，请检查是否IP被ban或header头被禁用")
        exit()
    return data.text

#session = login_web(login_url)
citiao = sys.argv[1].split('，')
res_data = {'status':1}
for ci in citiao:
    html_text = get_html_by_ci(ci)
    ci = base64.b64decode(ci.encode('utf-8'))
    ci = str(ci,'utf-8')
    seletor = etree.HTML(html_text)
    bidding_company_nums = seletor.xpath("//div[contains(@class, 'Fn-ui-list')]/*/dd/*/a[@title='"+ci+"']/../../../dd[3]/a/text()")[0].strip() #竞价公司数量
    baidu_index_nums = seletor.xpath("//div[contains(@class, 'Fn-ui-list')]/*/dd/*/a[@title='"+ci+"']/../../../dd[5]/text()")[0].strip() #百度指数
    ci = urllib.parse.quote(ci)
    res_data.update({ci: {"bidding_company_nums" : bidding_company_nums, "baidu_index_nums" : baidu_index_nums}})
print(json.dumps(res_data))
