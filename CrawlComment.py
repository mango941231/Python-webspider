import requests
import re
import json
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
}
def geturl():
    channels = ['jc','gn','gj','cj','kj','ty','yl','qc','yx','shuo','qz','wj','gy','fo','tousu','sf','sh']
    url = 'https://news.sina.com.cn/c/2018-11-06/doc-ihmutuea7355537.shtml'
    # url = 'https://finance.sina.com.cn/roll/2018-11-07/doc-ihmutuea7787670.shtml'
    p1 = re.compile(r'doc-i(.*?).shtml', re.S)
    cuturl = re.findall(p1, url)
    cmnt_list = []
    for i in range(1,99):
        for c in channels:    #遍历正确的js页
            pageurl = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel={0}&newsid=comos-{1}&group=&compress=0&ie=gbk&oe=gbk&page={2}&page_size=20&jsvar=loader_1541659646912_32229203'.format(
                c, cuturl[0],i)
            if len(requests.get(pageurl,headers=headers).text) > 1000:
                response = requests.get(pageurl,headers=headers).text
                p2 = re.compile(r'=(.*)', re.S)
                cutjson = re.findall(p2, response)
                respjson = cutjson[0]

                html = json.loads(respjson)
                cmnt_items = html['result']['cmntlist']     #最新评论
                hot_items = html['result']['hot_list']  # 最热评论
                for cmnt in cmnt_items:
                    Name = cmnt['nick']                 #名称
                    Area = cmnt['area']                 #位置
                    Time = cmnt['time']                 #评论时间
                    cmnt_list.append({'Name':Name,'Area':Area,'Time':Time})
        if cmnt_items == []:
            break
    # print(cmnt_list)
    hot_list = []
    for hot in hot_items:
        Name = hot['nick']  # 名称
        Area = hot['area']  # 位置
        Time = hot['time']  # 评论时间
        hot_list.append({'Name':Name,'Area':Area,'Time':Time})
    comment_dict = {'最新评论':cmnt_list,'最火评论':hot_list}
    # print(hot_list)
    print(comment_dict)











if __name__ == '__main__':
    geturl()