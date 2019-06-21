import requests
from lxml import etree
import pymongo
import pandas as pd
from urllib.request import urlretrieve
from bbs_crawler import bbs_spider

url = 'http://i.dxy.cn/profile/'
MONGO_URI = 'localhost'
MONGO_DB = 'test'
MONGO_COLLECTION = 'dxy'
user = 'yilizhongzi'


class dxy_spider(object):
    def __init__(self, user_id, mongo_uri, mongo_db):
        self.url = url + user_id
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[MONGO_DB]

    def get_html(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        req = requests.get(self.url, headers=headers).text
        # print(req)
        return req

    def get_UserInfo(self):
        raw_html = self.get_html()
        selector = etree.HTML(raw_html)
        key_list = []
        value_list = []
        force_fan_dd_key = selector.xpath('//div[@class="follows-fans clearfix"]//p/text()')
        force_fan_dd_value = selector.xpath('//div[@class="follows-fans clearfix"]//p/a/text()')

        if '关注' in force_fan_dd_key:
            for each in force_fan_dd_key:
                key_list.append(each)
        #             print(key_list)
            for each in force_fan_dd_value:
                value_list.append(each)
        #             print(value_list)
        else:
            key_list = ['关注', '粉丝', '丁当']
            value_list = ['0', '0', '0']

        UserInfo_dict = dict(zip(key_list, value_list))
        #         print(UserInfo_dict) #{'关注': '28', '粉丝': '90', '丁当': '1128}

        try:
            user_home = selector.xpath('//p[@class="details-wrap__items"]/text()')[0]
            UserInfo_dict['地址'] = user_home
        except IndexError as e:
            UserInfo_dict['地址'] = '无'
            print('地址缺少，报错！')

        try:
            user_profile = selector.xpath('//p[@class="details-wrap__items details-wrap__last-item"]/text()')
            UserInfo_dict['座右铭'] = user_profile
        except IndexError as e:
            UserInfo_dict['座右铭'] = '无'
            print('地址缺少，报错！')
        # print(user_profile)
        # 帖子被浏览
        try:
            article_browser = selector.xpath(
                '//li[@class="statistics-wrap__items statistics-wrap__item-topic fl"]/p/text()')
            UserInfo_dict['article_browser'] = article_browser[1]
        except IndexError as e:
            UserInfo_dict['article_browser'] = '无'
            print('article_browser缺少，报错！')

        # 帖子被投票
        try:
            article_vote = selector.xpath(
                '//li[@class="statistics-wrap__items statistics-wrap__item-vote fl"]/p/text()')
            UserInfo_dict['article_vote'] = article_vote[1]
        except IndexError as e:
            UserInfo_dict['article_vote'] = '无'
            print('article_vote缺少，报错！')

        # 帖子被收藏
        try:
            article_collect = selector.xpath(
                '//li[@class="statistics-wrap__items statistics-wrap__item-fav fl"]/p/text()')
            UserInfo_dict['article_collect'] = article_collect[1]
        except IndexError as e:
            UserInfo_dict['article_collect'] = '无'
            print('article_collect缺少，报错！')

        # 在线时长共
        try:
            onlie_time = selector.xpath(
                '//li[@class="statistics-wrap__items statistics-wrap__item-time fl"]/p/text()')
            UserInfo_dict['onlie_time'] = onlie_time[1]
        except IndexError as e:
            UserInfo_dict['onlie_time'] = '无'
            print('onlie_time缺少，报错！')

        # print(UserInfo_dict)
        return UserInfo_dict

    def Save_MongoDB(self, userinfo):
        self.db[MONGO_COLLECTION].insert(userinfo)
        self.client.close()

    def Save_Excel(self, userinfo):
        key_list = []
        value_list = []
        for key, value in userinfo.items():
            key_list.append(key)
            value_list.append(value)
        key_list.insert(0, '用户名')
        value_list.insert(0, user)
        data = pd.DataFrame(data=[value_list], columns=key_list)
        print(data)
        '''
        表示以用户名命名csv文件，并去掉DataFame序列化后的index列(这就是index=False的意思)，并以utf-8编码，
        防止中文乱码。
        注意：一定要先用pandas的DataFrame序列化后，方可使用to_csv方法导出csv文件！
        '''
        data.to_csv('./each/' + user + '.csv', encoding='utf_8_sig', index=False)

    def downloadavater(self, bbs_avater, bbs_id):
        urlretrieve(bbs_avater, './data/{0}.jpg'.format(bbs_id))


if __name__ == "__main__":
    raw_id = '3927842'
    bbs = bbs_spider(raw_id)
    bbs_id, bbs_avater = bbs.del_repeat_id(raw_id)
    print("-------------------------------")
    print(bbs_id)
    print(len(bbs_id))
    print(bbs_avater)
    print(len(bbs_avater))

    i = 0

    for user in bbs_id:
        dxy = dxy_spider(user, MONGO_URI, MONGO_DB)
        userinfo = dxy.get_UserInfo()
        print('***************')
        print(userinfo)
        dxy.Save_MongoDB(userinfo)
        dxy.downloadavater(bbs_avater[i], user)
        dxy.Save_Excel(userinfo)

        # 合并each里面所有的单个用户数据，并存储至all.csv
        df = pd.read_csv('./each/' + user + '.csv', engine='python', encoding='utf_8_sig')
        if i == 0:
            df.to_csv('all.csv', encoding="utf_8_sig", index=False, mode='a+', header=True)
        else:
            df.to_csv('all.csv', encoding="utf_8_sig", index=False, mode='a+', header=False)
        i += 1