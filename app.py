from flask import Flask
import requests
import re
import json
import time
import asyncio
import aiohttp
from flask import request
from pyquery import PyQuery as pq
from urllib import parse
from collections import OrderedDict
import threading
import random
import cookies
import datetime

app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def abc():
    url = request.values.get('pageurl')
    if 'sina' in url:
        a = Sina_Comment(url).main()
    elif 'sohu' in url:
        a = Sh_Comment(url).main()
    elif 'ifeng' in url:
        a = Fh_Comment(url).main()
    elif '163.com' in url:
        a = Wy_Comment(url).main()
    elif 'qq.com' in url:
        a = Tx_Comment(url).main()
    elif 'weibo' in url:
        a = Wb_Comment(url).main()
    return json.dumps(a,ensure_ascii=False)
"""新浪新闻"""
class Sina_Comment:
    def __init__(self,url):
        self.url = url
        self.cmnt_list = []
        self.hot_list = []
        self.headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
}

    async def geturl(self,i,u):
        channels = ['jc', 'gn', 'gj', 'cj', 'kj', 'ty', 'yl', 'qc', 'yx', 'shuo', 'qz', 'wj', 'gy', 'fo', 'tousu', 'sf',
                    'sh','pl']
        url = u
        # url = 'https://finance.sina.com.cn/roll/2018-11-07/doc-ihmutuea7787670.shtml'
        p1 = re.compile(r'-i(.*?).shtml', re.S)
        cuturl = re.findall(p1, url)
        for c in channels:  # 遍历正确的js页
            pageurl = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={0}&newsid=comos-{1}&group=&compress=0&ie=gbk&oe=gbk&page={2}&page_size=20&jsvar=loader_1541659646912_32229203'.format(
                c, cuturl[0], i)
            async with aiohttp.ClientSession() as session:
                async with session.get(pageurl, headers=self.headers) as html:
                    response = await html.text(encoding="utf-8")
                    if len(response) > 1000:
                        return response

    async def parse(self,page,u):
        response = await self.geturl(page,u)
        p2 = re.compile(r'=(.*)', re.S)
        cutjson = re.findall(p2, response)
        respjson = cutjson[0]
        html = json.loads(respjson)
        cmnt_items = html['result']['cmntlist']  # 最新评论
        hot_items = html['result']['hot_list']  # 最热评论
        for cmnt in cmnt_items:
            Mid = cmnt['mid']    #ID
            Name = cmnt['nick']  # 名称
            Area = cmnt['area']  # 位置
            Time = cmnt['time']  # 评论时间
            Content = cmnt['content']  #评论内容
            Newsid = cmnt['newsid']     #Newsid
            Agree = cmnt['agree']       #点赞数
            self.cmnt_list.append({'Mid':Mid,'Newsid':Newsid,'Name': Name, 'Area': Area, 'Content':Content, 'Agree':Agree,'Time': Time})
        for hot in hot_items:
            Mid = hot['mid']     #ID
            Name = hot['nick']  # 名称
            Area = hot['area']  # 位置
            Time = hot['time']  # 评论时间
            Content = hot['content']  # 评论内容
            Newsid = cmnt['newsid']  # Newsid
            Agree = cmnt['agree']  # 点赞数
            if len(self.hot_list) < 3:
                self.hot_list.append({'Mid':Mid,'Newsid':Newsid,'Name': Name, 'Area': Area, 'Content':Content, 'Agree':Agree, 'Time': Time})
            else:
                break
    def main(self):
        T1 = time.time()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        tasks = [self.parse(i,self.url) for i in range(1, 50)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        T2 = time.time()
        sina_commment_dict = {'最新评论': self.cmnt_list, '最热评论': self.hot_list,'type':'xinlang'}
        return sina_commment_dict

"""搜狐新闻"""
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
            # Source_id = html['jsonObject']['source_id']
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
                    # Source_id = html['jsonObject']['source_id']
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

"""凤凰新闻"""
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

"""网易新闻"""
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

    def get_hot(self):

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
            page_url = 'http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{0}/comments/hotList?{1}'.format(self.cuturl[0],data)
            response = requests.get(page_url).text
            p2 = re.compile(r'[(]\n(.*)[)]', re.S)
            cut_json = re.findall(p2, response)
            page_json = cut_json[0]
            html = json.loads(page_json)
            hot_comments = html['comments']
            hot_html = dict(hot_comments)
            for hot in hot_html.values():
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
            async with session.get(pageurl) as pagehtml:
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
        self.get_hot()
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

"""腾讯新闻"""
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

"""新浪微博"""
# class Wb_Comment:
#     def __init__(self,url):
#         self.url = url
#         self.news_list = []
#         self.headers = {
#     'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Mobile Safari/537.36',
#     'Cookie':random.choice(cookies.cookies),
#
# }
#     async def get_comment(self,page):
#         p1 = re.compile(r'.*/(.*)', re.S)
#         cuturl = re.findall(p1, self.url)
#         pageurl = 'https://m.weibo.cn/api/comments/show?id={0}&page={1}'.format(cuturl[0],page)
#         async with aiohttp.ClientSession() as session:
#             async with session.get(pageurl,headers=self.headers) as pagehtml:
#                 response = await pagehtml.text("utf-8","ignore")
#                 html = json.loads(response)
#                 if html['ok'] != 0:
#                     items = html['data']['data']
#                     for item in items:
#                         content = item['text']
#                         p2 = re.compile('</?\w+[^>]*>')
#                         Content = re.sub(p2, '', content)  # 评论内容
#                         Mid = item['id']  # 评论ID
#                         creatat = item['created_at']  # 评论时间
#                         i = datetime.datetime.now()
#                         if '时' in creatat:
#                             p2 = re.compile(r'(.*)小时前', re.S)
#                             timenum = re.findall(p2,creatat)
#                             if int(timenum[0]) > i.hour:
#                                 Time = str(i.year) + '-' + str(i.month) + '-' + str(i.day-(timenum[0]/24)) + ' ' + str(
#                                     24-(int(timenum[0]) % i.hour)) + ':' + str(i.minute) + ':' + str(i.second)
#                             else:
#                                 Time = str(i.year) + '-' + str(i.month) + '-' + str(i.day) + ' ' + str(i.hour-int(timenum[0])) + ':' + str(i.minute) + ':' + str(i.second)
#                         elif '分' in creatat:
#                             p2 = re.compile(r'(.*)分钟前', re.S)
#                             timenum = re.findall(p2, creatat)
#                             if int(timenum[0]) > i.minute:
#                                 Time = str(i.year) + '-' + str(i.month) + '-' + str(i.day) + ' ' + str(i.hour - 1) + ':' + str(60-(int(timenum[0])-i.minute)) + ':' + str(i.second)
#                             else:
#                                 Time = str(i.year) + '-' + str(i.month) + '-' + str(i.day) + ' ' + str(i.hour - 1) + ':' + str(i.minute-int(timenum[0])) + ':' + str(i.second)
#                         elif '昨' in creatat:
#                             p2 = re.compile(r'昨天(.*)', re.S)
#                             timenum = re.findall(p2, creatat)
#                             Time = str(i.year) + '-' + str(i.month) + '-' + str(i.day-1) + ' ' + str(timenum[0])
#                         elif '刚刚' in creatat:
#                             Time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                         else:
#                             Time = creatat
#                         Name = item['user']['screen_name']  # 名称
#                         Agree = item['like_counts']
#                         self.news_list.append({'ID': Mid, 'Name': Name, 'Content': Content,'Agree':Agree, 'Time': Time})
#                         # print(len(self.news_list))
#
#     def get_pagesnum(self):
#         p1 = re.compile(r'.*/(.*)', re.S)
#         cuturl = re.findall(p1, self.url)
#         pageurl = 'https://m.weibo.cn/api/comments/show?id={0}&page=1'.format(cuturl[0])
#         response = requests.get(pageurl,headers=self.headers).text
#         html = json.loads(response)
#         try:
#             pages = html['data']['total_number']
#             return pages
#         except KeyError:
#             print('IP限制访问')
#     '''
#     def get_ip_list(self):
#         print("正在获取代理列表...")
#         url = 'http://www.xicidaili.com/nn/'
#         html = requests.get(url=url, headers=headers).text
#         soup = BeautifulSoup(html, 'lxml')
#         ips = soup.find(id='ip_list').find_all('tr')
#         ip_list = []
#         for i in range(1, len(ips)):
#             ip_info = ips[i]
#             tds = ip_info.find_all('td')
#             ip_list.append(tds[1].text + ':' + tds[2].text)
#         print("代理列表抓取成功.")
#         return ip_list
#
#     def get_random_ip(self, ip_list):
#         print("正在设置随机代理...")
#         proxy_list = []
#         for ip in ip_list:
#             proxy_list.append('http://' + ip)
#         proxy_ip = random.choice(proxy_list)
#         proxies = {'http': proxy_ip}
#         print("代理设置成功.")
#         return proxies
#     '''
#     def main(self):
#         try:
#             # T1 = time.time()
#             # iplist = self.get_ip_list()
#             # randomip = self.get_random_ip(iplist)
#             pagenum = self.get_pagesnum()
#             asyncio.set_event_loop(asyncio.new_event_loop())
#             # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
#             loop = asyncio.get_event_loop()
#             tasks = [self.get_comment(i) for i in range(1,int(pagenum/10+5))]
#             loop.run_until_complete(asyncio.wait(tasks))
#             loop.close()
#             # T2 = time.time()
#             # wb_comment_dict = {'最新评论':len(self.news_list)}
#             wb_comment_dict = {'最新评论': self.news_list,'type':'xinlangweibo'}
#             # print(wb_comment_dict)
#             # print(T2-T1)
#             return wb_comment_dict
#         except TypeError as e:
#             print(e)
class Wb_Comment:
    def __init__(self,url):
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Mobile Safari/537.36',
            'Cookie':random.choice(cookies.cookies)
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
            timeArray = datetime.datetime.strptime(Time, '%a %b %d %H:%M:%S +0800 %Y')
            otherStyleTime = timeArray.strftime(
                '%Y/%m/%d %H:%M:%S')  # 评论时间  Tue Nov 20 12:39:24 +0800 2018 转为 2018/11/20 12:39:24 格式
            self.comment_list.append({'ID': ID, 'Name': Name, 'Content': Content,'Agree':Agree, 'Time': otherStyleTime})
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
                    maxid = html['data']['max_id']
                    if maxid == 0:
                        break
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

    def main(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_next())
        loop.close()
        # wb_commment_dict = {'最新评论': len(self.comment_list)}
        wb_commment_dict = {'最新评论': self.comment_list,'type': 'xinlangweibo'}
        # print(wb_commment_dict)
        return wb_commment_dict

if __name__ == '__main__':
    app.run()
