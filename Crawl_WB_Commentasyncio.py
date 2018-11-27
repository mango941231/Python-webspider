"""最终版2018/11/27（修改了只能爬最新的 不能爬'昨天'的评论内容 测试表示微博限制单个用户访问频次较严重 本次添加了五个Cookie）"""
import requests
import json
import re
import ceshi.cookies as ck
import random
import aiohttp
import asyncio
class Wb_Comment:
    def __init__(self,url):
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Mobile Safari/537.36',
            'Cookie':random.choice(ck.cookies)
        }
        self.url = url
        self.comment_list = []
        p1 = re.compile(r'.*/(.*)', re.S)
        cuturl = re.findall(p1, self.url)
        self.mid = cuturl[0]
    def get_frist(self):
        url = 'https://m.weibo.cn/comments/hotflow?id={0}&mid={0}&max_id_type=0'.format(self.mid)
        response = requests.get(url,headers=self.headers).text
        html = json.loads(response)
        items = html['data']['data']
        for item in items:
            ID = item['id']
            Name = item['user']['screen_name']
            Content = item['text']
            Agree = item['like_count']
            Time = item['created_at']
            self.comment_list.append({'ID': ID, 'Name': Name, 'Content': Content,'Agree':Agree, 'Time': Time})
        next_id = html['data']['max_id']
        return next_id
    async def get_next(self):
        maxid = self.get_frist()
        while 1:
            url = 'https://m.weibo.cn/comments/hotflow?id={0}&mid={0}&max_id={1}&max_id_type=0'.format(self.mid,maxid)
            async with aiohttp.ClientSession() as session:
                async  with session.get(url,headers=self.headers) as pagehtml:
                    response = await pagehtml.text("utf-8", "ignore")
                    html = json.loads(response)
                    items = html['data']['data']
                    for item in items:
                        ID = item['id']
                        Name = item['user']['screen_name']
                        Content = item['text']
                        Agree = item['like_count']
                        Time = item['created_at']
                        timeArray = datetime.datetime.strptime(Time, '%a %b %d %H:%M:%S +0800 %Y')
                        otherStyleTime = timeArray.strftime(
                            '%Y/%m/%d %H:%M:%S')  # 评论时间  Tue Nov 20 12:39:24 +0800 2018 转为 2018/11/20 12:39:24 格式
                        self.comment_list.append({'ID': ID, 'Name': Name, 'Content': Content, 'Agree': Agree, 'Time': otherStyleTime})
                    maxid = html['data']['max_id']
                    if maxid == 0:
                        break
    def main(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_next())
        loop.close()
        # wb_commment_dict = {'最新评论': len(self.comment_list)}
        wb_commment_dict = {'最新评论': self.comment_list,'type': 'weibo'}
        # print(wb_commment_dict)
        return wb_commment_dict


