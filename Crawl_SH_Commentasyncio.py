"""最终版2018/11/23"""
import requests
from pyquery import PyQuery as pq
from urllib import parse
import re
import json
import time
import asyncio
import aiohttp
class Sh_Comment:
    def __init__(self,url):
        self.url = url
        resp = requests.get(self.url).text
        doc = pq(resp)
        self.topic_title = doc('.wrapper-box .text-title h1').text()  # topic_title
        p = re.compile(r'.*/(.*?)_.*', re.S)
        cut = re.findall(p, self.url)
        self.source_id = 'mp_' + cut[0]                 # source_id
        self.hot_list = []
        self.cmnt_list = []

    def hot_comment(self):
        params = {
            'callback':'jQuery1124039668336202851107_1542852755754',
            'page_size':10,
            'topic_source_id':556070408,
            'page_no':1,
            'hot_size':5,
            'media_id':255783,
            'topic_category_id':8,
            'topic_title':self.topic_title,
            'topic_url':self.url,
            'source_id':self.source_id,
            '_':1542852755787
        }
        data = parse.urlencode(params)
        pageurl = 'http://apiv2.sohu.com/api/topic/load?{}'.format(data)
        response = requests.get(pageurl).text
        p1 = re.compile(r'[(](.*)[)]', re.S)
        pagejson = re.findall(p1,response)
        html = json.loads(pagejson[0])
        hots = html['jsonObject']['hots']
        for hot in hots:
            Content = hot['content']
            Comment_id = hot['comment_id']
            Name = hot['passport']['nickname']
            createtime = str(hot['create_time'])
            Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(createtime[:10])))  # Unix时间戳转指定格式日期
            Agree = hot['support_count']
            Topic_id = html['jsonObject']['topic_id']
            self.hot_list.append({'Comment_id':Comment_id,'Name': Name,'Content':Content,'Agree':Agree,'Time':Time,'Source_id':self.source_id,'Topic_id':Topic_id})
        cmtnum = html['jsonObject']['cmt_sum']    #总评论数
        return cmtnum
    async def cmnt_comment(self,page):
        #url = 'http://apiv2.sohu.com/api/comment/list?callback=jQuery112409852257395190231_1542855061411&page_size=10&topic_id=13061055&page_no=2&source_id=mp_277020480&_=1542855061439'
        params = {
            'callback': 'jQuery1124039668336202851107_1542852755754',
            'page_size': 10,
            'topic_id': 13061055,
            'page_no': page,
            'source_id': self.source_id,
            '_': 1542855061439
        }
        data = parse.urlencode(params)
        pageurl = 'http://apiv2.sohu.com/api/comment/list?{}'.format(data)
        async with aiohttp.ClientSession() as session:
            async with session.get(pageurl) as pagehtml:
                response = await pagehtml.text(encoding="utf-8")
                p1 = re.compile(r'[(](.*)[)]', re.S)
                pagejson = re.findall(p1, response)
                html = json.loads(pagejson[0])
                cmnts = html['jsonObject']['comments']
                for cmnt in cmnts:
                    Content = cmnt['content']
                    Comment_id = cmnt['comment_id']
                    Name = cmnt['passport']['nickname']
                    createtime = str(cmnt['create_time'])
                    Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(createtime[:10])))  # Unix时间戳转指定格式日期
                    Agree = cmnt['support_count']
                    Topic_id = html['jsonObject']['topic_id']
                    self.cmnt_list.append({'Comment_id': Comment_id, 'Name': Name, 'Content': Content, 'Agree': Agree, 'Time': Time,'Source_id':self.source_id,'Topic_id':Topic_id})
    def main(self):
        pages = self.hot_comment()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        tasks = [self.cmnt_comment(i) for i in range(1,int(int(pages)/10+2))]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        sh_commment_dict = {'最新评论': self.cmnt_list, '最热评论': self.hot_list,'type':'souhu'}
        # sh_commment_dict = {'最新评论': len(self.cmnt_list), '最热评论': len(self.hot_list)}
        # print(sh_commment_dict)
        return sh_commment_dict