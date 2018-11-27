import requests
import re
import json
import time
import asyncio
import aiohttp
from urllib import parse

class Tx_Comment:
    def __init__(self, url):
        self.url = url
        self.hot_list = []
        self.new_list = []
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
        }
        '''分析多种不同的腾讯新闻链接'''
        try:
            if 'news' in self.url:
                html = requests.get(self.url,headers=self.headers).text
                p1 = re.compile(r'cmt_id = (.*?);', re.S)
                cutjson = re.findall(p1, html)
                self.comid = cutjson[0]
            elif len(self.url.split('/')) == 5:
                p1 = re.compile(r'.*/(.*)', re.S)
                cutpara = re.findall(p1, self.url)
                param = {
                    'id': cutpara[0],
                    'chlid': 'news_rss',
                    'refer': 'mobilewwwqqcom',
                    'otype': 'jsonp',
                    'ext_data': 'all',
                    'srcfrom': 'newsapp',
                    'callback': 'getNewsContentOnlyOutput'
                }
                # https: // openapi.inews.qq.com / getQQNewsNormalContent?id = NEW2018112201551000 & chlid = news_rss & refer = mobilewwwqqcom & otype = jsonp & ext_data = all & srcfrom = newsapp & callback = getNewsContentOnlyOutput
                paradata = parse.urlencode(param)
                paraurl = 'https://openapi.inews.qq.com/getQQNewsNormalContent?{}'.format(paradata)
                html = requests.get(paraurl,headers=self.headers).text
                p2 = re.compile(r'[(](.*)[)]', re.S)
                cutparajson = re.findall(p2, html)
                parajson = json.loads(cutparajson[0])
                self.comid = parajson['cid']
            else:
                html = requests.get(self.url).text
                p1 = re.compile(r'window.DATA = (.*?)}', re.S)
                cutjson = re.findall(p1, html)
                if cutjson:
                    p2 = re.sub('[\t\n]', '', cutjson[0])
                    p3 = p2 + '}'
                    p4 = json.loads(p3)
                    self.comid = p4['comment_id']
                else:
                    p5 = re.compile(r'.*/(.*)', re.S)
                    cutpara = re.findall(p5, self.url)
                    param = {
                        'id': cutpara[0],
                        'chlid': 'news_rss',
                        'refer': 'mobilewwwqqcom',
                        'otype': 'jsonp',
                        'ext_data': 'all',
                        'srcfrom': 'newsapp',
                        'callback': 'getNewsContentOnlyOutput'
                    }
                    # https: // openapi.inews.qq.com / getQQNewsNormalContent?id = NEW2018112201551000 & chlid = news_rss & refer = mobilewwwqqcom & otype = jsonp & ext_data = all & srcfrom = newsapp & callback = getNewsContentOnlyOutput
                    paradata = parse.urlencode(param)
                    paraurl = 'https://openapi.inews.qq.com/getQQNewsNormalContent?{}'.format(paradata)
                    html = requests.get(paraurl,headers=self.headers).text
                    p2 = re.compile(r'[(](.*)[)]', re.S)
                    cutparajson = re.findall(p2, html)
                    parajson = json.loads(cutparajson[0])
                    self.comid = parajson['cid']
        except Exception:
            print('链接格式错误')

    def get_hot(self):
        params = {
            'callback': '_article{}commentv2'.format(self.comid),
            'orinum': 10,
            'oriorder': 'o',
            'pageflag': 1,
            'cursor': 0,
            'scorecursor': 0,
            'orirepnum': 2,
            'reporder': 'o',
            'reppageflag': 1,
            'source': 1,
            '_': 1542339702912
        }
        data = parse.urlencode(params)
        page_url = 'http://coral.qq.com/article/{}/comment/v2?{}'.format(self.comid, data)
        response = requests.get(page_url,headers=self.headers).text
        p5 = re.compile(r'[(](.*)[)]', re.S)
        hot_json = re.findall(p5, response)
        page_json = hot_json[0]
        hot_html = json.loads(page_json)
        hot_comments = hot_html['data']['oriCommList']
        users = hot_html['data']['userList']
        user_sd = dict(users)
        for hot in hot_comments:
            for u in user_sd.values():
                if hot['userid'] == u['userid']:
                    Name = u['nick']
                    Area = u['region']
                    Content = hot['content']
                    ID = hot['id']
                    Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(hot['time'])))  # Unix时间戳转指定格式日期
                    self.hot_list.append({'ID': ID, 'Name': Name, 'Area': Area, 'Content': Content, 'Time': Time})

    async def getnews(self):
        cursor = 0
        while 1:
            params = {
                'callback': '_article{}commentv2'.format(self.comid),
                'orinum': 10,
                'oriorder': 't',
                'pageflag': 1,
                'cursor': cursor,
                'scorecursor': 0,
                'orirepnum': 2,
                'reporder': 'o',
                'reppageflag': 1,
                'source': 1,
                '_': 1542339702912
            }
            data = parse.urlencode(params)
            pageurl = 'http://coral.qq.com/article/{}/comment/v2?{}'.format(self.comid, data)
            async with aiohttp.ClientSession() as session:
                async with session.get(pageurl,headers=self.headers) as pagehtml:
                    response = await pagehtml.text("utf-8", "ignore")
                    p5 = re.compile(r'[(](.*)[)]', re.S)
                    newjson = re.findall(p5, response)
                    pagejson = newjson[0]
                    newhtml = json.loads(pagejson)
                    newcomments = newhtml['data']['oriCommList']
                    if newcomments == []:
                        break
                    else:
                        users = newhtml['data']['userList']
                        usersd = dict(users)
                        for new in newcomments:
                            for u in usersd.values():
                                if new['userid'] == u['userid']:
                                    Name = u['nick']
                                    Area = u['region']
                                    Content = new['content']
                                    ID = new['id']
                                    Time = time.strftime("%Y-%m-%d %H:%M:%S",
                                                         time.localtime(int(new['time'])))  # Unix时间戳转指定格式日期
                                    self.new_list.append(
                                        {'ID': ID, 'Name': Name, 'Area': Area, 'Content': Content, 'Time': Time})
                        cursor = newhtml['data']['last']

    def main(self):
        self.get_hot()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.getnews())
        loop.close()
        # tx_commment_dict = {'最新评论': len(self.new_list), '最热评论': len(self.hot_list)}
        tx_commment_dict = {'最新评论': self.new_list, '最热评论': self.hot_list, 'type': 'tengxun'}
        # print(tx_commment_dict)
        return tx_commment_dict