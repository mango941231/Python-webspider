"""最终版2018/11/23"""
import re
import json
import asyncio
import aiohttp
import requests
from urllib import parse
# headers = {
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
# }
class Fh_Comment:
    def __init__(self,url):
        self.url = url
        self.cmnt_list = []
        self.hot_list = []
        params = {
            'callback': 'newCommentListCallBack',
            'orderby': '',
            'docUrl': self.url,
            'format': 'js',
            'job': 1,
            'p': 1,
            'pageSize': 20,
            'callback': 'newCommentListCallBack',
            'skey': '38eaaf'
        }
        data = parse.urlencode(params)
        pageurl = 'https://comment.ifeng.com/get.php?{}'.format(data)
        response = requests.get(pageurl).text
        p1 = re.compile(r'=(.*?)};', re.S)
        cuturl = re.findall(p1, response)
        commentjson = cuturl[0] + "}"
        html = json.loads(commentjson)
        '''处理多种链接不同的情况 比如财经、娱乐等栏目和资讯链接不同'''
        if html['comments'] == []:
            resp = requests.get(url).text
            p2 = re.compile(r'"commentUrl":"(.*?)",', re.S)
            cut = re.findall(p2, resp)
            self.url = cut[0]
            params = {
                'callback': 'newCommentListCallBack',
                'orderby': '',
                'docUrl': cut[0],
                'format': 'js',
                'job': 1,
                'p': 1,
                'pageSize': 20,
                'callback': 'newCommentListCallBack',
                'skey': '38eaaf'
            }
            data = parse.urlencode(params)
            pageurl = 'https://comment.ifeng.com/get.php?{}'.format(data)
            response = requests.get(pageurl).text
            p1 = re.compile(r'=(.*?)};', re.S)
            cuturl = re.findall(p1, response)
            commentjson = cuturl[0] + "}"
            html = json.loads(commentjson)
        self.pages = int(html['count'] / 20) + 2

    async def get_cmnt(self,pg):
        pagesparms = {
            'callback': 'newCommentListCallBack',
            'orderby': '',
            'docUrl': self.url,
            'format': 'js',
            'job': 1,
            'p': pg,
            'pageSize': 20,
            'callback': 'newCommentListCallBack',
            'skey': '38eaaf'
        }
        pagesdata = parse.urlencode(pagesparms)
        pagesurl = 'https://comment.ifeng.com/get.php?{}'.format(pagesdata)
        async with aiohttp.ClientSession() as session:
            async with session.get(pagesurl) as pageshtml:
                pagesresponse = await pageshtml.text(encoding="utf-8")
                p2 = re.compile(r'=(.*?)};', re.S)
                pagescuturl = re.findall(p2, pagesresponse)
                pagescommentjson = pagescuturl[0] + "}"
                pageshtml = json.loads(pagescommentjson)
                comments = pageshtml['comments']
                for com in comments:
                    CmtID = com['comment_id'] #评论ID
                    Name = com['uname']     #名称
                    Area = com['ip_from']   #位置
                    Content = com['comment_contents']   #评论内容
                    Time = com['comment_date']
                    Doc_url = com['doc_url']
                    self.cmnt_list.append({'CmtID':CmtID,'Name':Name,'Area':Area,'Content':Content,'Time':Time,'Docurl':Doc_url})
    def get_hot(self):
        parms = {
            'callback': 'hotCommentListCallBack',
            'orderby': 'uptimes',
            'docUrl': self.url,
            'format': 'js',
            'job': 1,
            'p': 1,
            'pageSize': 10,
            'callback': 'hotCommentListCallBack',
            'skey': '38eaaf'
        }
        data = parse.urlencode(parms)
        pageurl = 'https://comment.ifeng.com/get.php?{}'.format(data)
        response = requests.get(pageurl).text
        p1 = re.compile(r'=(.*?)};', re.S)
        cuturl = re.findall(p1, response)
        commentjson = cuturl[0] + "}"
        html = json.loads(commentjson)
        hotcomments = html['comments']
        for hot in hotcomments:
            CmtID = hot['comment_id']  # 评论ID
            Name = hot['uname']  # 名称
            Area = hot['ip_from']  # 位置
            Content = hot['comment_contents']  # 评论内容
            Time = hot['comment_date']  # 评论时间
            Doc_url = hot['doc_url']
            self.hot_list.append({'CmtID': CmtID, 'Name': Name, 'Area': Area, 'Content': Content, 'Time': Time,'Docurl':Doc_url})
    def main(self):
        self.get_hot()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        tasks = [self.get_cmnt(i) for i in range(1,self.pages)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        fh_commment_dict = {'最新评论': self.cmnt_list, '最热评论': self.hot_list, 'type': 'fenghuang'}
        # fh_commment_dict = {'最新评论': len(self.cmnt_list), '最热评论': len(self.hot_list)}
        # print(fh_commment_dict)
        return fh_commment_dict
