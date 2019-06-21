import requests
from lxml import etree

url = 'http://www.dxy.cn/bbs/topic/'


class bbs_spider(object):
    def __init__(self, id):
        self.url = url + id

    def get_html(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': '__utmz=251724881.1560424067.2.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=251724881.2047513055.1544518931.1544518931.1560424067.2; Hm_lvt_253e434fd63b62a2659ddd3e7412f769=1560424066; __utmz=1.1560829440.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_8a6dad3652ee53a288a11ca184581908=1560829440,1560950901; DXY_USER_GROUP=63; __utma=1.1757414799.1560829440.1560829440.1560829440.1; __auc=28377ff11679c7fa877ccb1dae0; JUTE_BBS_DATA=fe9c1fd2d8679d57b1f6e174c3a0e851768ec8e3d35b630a8c37365e24da47270c16cea209e3d94a67ff288b9f76320a0fab209c2cb2b1dd55879d2a2e1d4fa5af7b2501a8ef8e3d6732a8612a8ea00e; _ga=GA1.2.1757414799.1560829440; JUTE_SESSION_ID=5eb7c57a-a470-4f01-97ce-17ba935ef1a9; JUTE_TOKEN=cca6ff0a-bdb0-4e6b-80cc-e80a5e6e744b; JUTE_SESSION=82c9099c69c32fc62df37c5cdfeaaea9b3816aa145abeb548ba4de4b53de9e2ddb88d3ecbb3c4c9836253c2ed96549bd13b1d977977aaa7dc3a783c09f2dae1f8f2ebaef6e538b82; CMSSESSIONID=795890F0FA9A912046F369CC908DD3AD-n2; Hm_lpvt_8a6dad3652ee53a288a11ca184581908=1560950901; bannerData={"banner":false,"message":"²»ÏÔÊ¾banner"}',
            'Host': 'www.dxy.cn',
            'Referer': 'https://auth.dxy.cn/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        req = requests.get(self.url, headers=headers).text
        return req

    def get_bbsinfo(self):
        raw_html = self.get_html()
        selector = etree.HTML(raw_html)
        # title
        bbs_title = selector.xpath('//table[@class="title tbfixed"]/tbody/tr/th/h1/text()')[0]
        bbs_title = bbs_title.strip()  # 去除字符串左右的空格
        # photo
        bbs_other_avater = selector.xpath('//td[@class="tbs"]//div[@class="avatar"]/div/span/a/img/@src')
        # id
        bbs_other_id = selector.xpath('//td[@class="tbs"]//div[@class="auth"]/a/text()')

        try:
            page = selector.xpath('//div[@class="pages"]/div[@class="num"]/a[last()]/text()')[0]
        except IndexError as e:
            page = 1
        return bbs_other_id, bbs_other_avater, page

    def get_allpageurl(self, raw_id):
        bbs = bbs_spider(raw_id)
        bba_other_id, bbs_other_avater, page = bbs.get_bbsinfo()
        page_list = []
        for i in range(1, int(page) + 1):
            page_url = raw_id + '?ppg=' + str(i)
            page_list.append(page_url)
        return page_list

    # delete repeat id
    def del_repeat_id(self, raw_id):
        page_list = self.get_allpageurl(raw_id)
        data_bbs = {}
        for url in page_list:
            bbs = bbs_spider(url)
            bbs_id, bbs_avater, page = bbs.get_bbsinfo()
            bbs_data = dict(zip(bbs_id, bbs_avater))
            for key in bbs_data:
                if key not in data_bbs:
                    data_bbs[key] = bbs_data[key]

        bbs_id = []
        bbs_avater = []
        for key in data_bbs:
            bbs_id.append(key)
            bbs_avater.append(data_bbs[key])

        return bbs_id, bbs_avater


raw_id = '3927842'
bbs = bbs_spider(raw_id)
bbs_id, bbs_avater = bbs.del_repeat_id(raw_id)
print("-------------------------------")
print(bbs_id)
print(len(bbs_id))
print(bbs_avater)
print(len(bbs_avater))


