# Python-webspider
Framework technology used to crawl web page data and app data. selenium、mitmproxy（script）、APPium

#list
Crawl_XL_Commentasyncio.py  #sina news comments
Crawl_WY_Commentasyncio.py  #wangyi news comments
Crawl_WB_Commentasyncio.py  #weibo news comments
Crawl_TX_Commentasyncio.py  #tencent news comments
Crawl_SH_Commentasyncio.py  #souhu news comments
Crawl_FH_Commentasyncio.py  #fenghuang news comments
app.py #flask

app.py 采用flask web框架，生成接口,在浏览器输入域名+新闻网址 运行爬虫 采集评论，返回评论json数据。
所有采集均采用asyncio、aiohttp异步方式，大大提高采集速度。
