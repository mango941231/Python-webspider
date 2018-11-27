"""最终版2018/11/24"""
import re
import json
import asyncio
import aiohttp
import requests
from urllib import parse
from collections import OrderedDict
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
}
class Wy_Comment:
    def __init__(self,url):
        self.url = url
        self.hot_list = []
        self.new_list = []
        '''处理军事链接不同'''
        if 'photoview' in self.url:
            resp = requests.get(self.url).text
            p1 = re.compile(r'"docId" :  "(.*?)",', re.S)
            self.cuturl = re.findall(p1, resp)
        else:
            p3 = re.compile(r'.*/(.*).html', re.S)
            self.cuturl = re.findall(p3, self.url)  # 正则匹配出文章链接内特定的参数
        self.hocom_list = []
        self.hocom_list = []

    def gethot(self):

        t1 = [5, 35]
        t2 = [0, 5]
        for li,ft in zip(t1,t2):
            params = {
                'ibc':'newspc',
                'limit':li,
                'showLevelThreshold':72,
                'headLimit':1,
                'tailLimit':2,
                'offset':ft,
                'callback':'jsonp_1542251915219',
                '_':1542251915220
            }
            data = parse.urlencode(params)
            pageurl = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{0}/comments/hotList?{1}'.format(self.cuturl[0],data)
            response = requests.get(pageurl, headers=headers).text
            p2 = re.compile(r'[(]\n(.*)[)]', re.S)
            cutjson = re.findall(p2, response)
            pagejson = cutjson[0]
            html = json.loads(pagejson)
            hotcomments = html['comments']
            hothtml = dict(hotcomments)
            for hot in hothtml.values():
                CommentId = hot['commentId']            #评论ID
                Area = hot['user']['location']  #地区
                if 'nickname' in hot['user']:  #评论用户名
                    Name = hot['user']['nickname']
                else:
                    Name = '网易'+Area+'网友'
                Content = hot['content']         #评论内容
                Time = hot['createTime']        #评论时间
                ProductKey = hot['productKey']
                Agree = hot['vote']
                self.hot_list.append({'CommentId':CommentId,'Name': Name, 'Area': Area,'Content':Content,'Agree':Agree,'Time':Time,'ProductKey':ProductKey,'PostId':self.cuturl[0]})
        b = OrderedDict()
        for item in self.hot_list:
            b.setdefault(item['CommentId'],{**item,})
        self.hocom_list = list(b.values())            #最热评论
        for i in reversed(range(len(self.hocom_list))):
            if self.hocom_list[i].get('Content') == '跟贴被火星网友带走啦~':
                self.hocom_list.pop(i)

    async def getnews(self,page):
        params = {
            'ibc': 'newspc',
            'limit': 30,
            'showLevelThreshold': 72,
            'headLimit': 1,
            'tailLimit': 2,
            'offset': page,
            'callback': 'jsonp_1542251915219',
            '_': 1542251915220
        }
        data = parse.urlencode(params)
        pageurl = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{0}/comments/newList?{1}'.format(
            self.cuturl[0], data)
        async with aiohttp.ClientSession() as session:
            async with session.get(pageurl,headers=headers) as pagehtml:
                response = await pagehtml.text(encoding="utf-8")
                p2 = re.compile(r'[(]\n(.*)[)]', re.S)
                cutjson = re.findall(p2, response)
                pagejson = cutjson[0]
                html = json.loads(pagejson)
                newcomments = html['comments']
                newhtml = dict(newcomments)
                for new in newhtml.values():
                    CommentId = new['commentId']  # 评论ID
                    Area = new['user']['location']  # 地区
                    if 'nickname' in new['user']:  # 评论用户名
                        Name = new['user']['nickname']
                    else:
                        Name = '网易' + Area + '网友'
                    Content = new['content']  # 评论内容
                    Time = new['createTime']  # 评论时间
                    ProductKey = new['productKey']
                    Agree = new['vote']
                    self.new_list.append({'CommentId':CommentId,'Name': Name, 'Area': Area,'Content':Content,'Agree':Agree,'Time':Time,'ProductKey':ProductKey,'PostId':self.cuturl[0]})

    def main(self):
        self.gethot()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        tasks = [self.getnews(i*30) for i in range(55)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        b = OrderedDict()
        for item in self.new_list:
            b.setdefault(item['CommentId'], {**item, })
        self.new_list = list(b.values())
        for i in reversed(range(len(self.new_list))):
            if self.new_list[i].get('Content') == '跟贴被火星网友带走啦~':
                self.new_list.pop(i)
        wy_commment_dict = {'最新评论': self.new_list, '最热评论': self.hocom_list,'type':'wangyi'}
        # wy_commment_dict = {'最新评论': len(self.new_list), '最热评论': len(self.hocom_list)}
        # print(wy_commment_dict)
        return wy_commment_dict




