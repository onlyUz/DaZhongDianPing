# coding=utf-8
# @Time :  2021/1/23 20:13
# @Author : zjk
# @File : dazhong.py
# @software : PyCharm
import requests
import re
import pymongo
from lxml import etree


class AnalyticalData:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}

    def css_url(self, html_str):
        css_url = 'http://s3plus.meituan.net/v1/' + \
                  re.findall(r'href="//s3plus.meituan.net/v1/(.*?)">', html_str)[0]
        print(css_url)
        return css_url

    def svg_url(self, css_url):
        css_html = requests.get(css_url, headers=self.headers).text
        svg_url = 'http://s3plus.meituan.net/v1/' + re.findall(r'url\(//s3plus.meituan.net/v1/(.*?)\);', css_html)[1]
        print(svg_url)
        return svg_url

    def get_css_dict(self, css_url):
        """
        解析css
        :return: (name, 长度， 高度)
        """
        css_html = requests.get(css_url, headers=self.headers).text
        css_list = re.findall(r'.(\w+){background:-(\d+).0px -(\d+).0px;}', css_html)
        css_map = [(name, int(x), int(y)) for name, x, y in css_list]  # (name, 长度， 高度)
        return css_map

    def get_svg_dict(self, svg_url):
        """
        解析svg
        :return: ('height': 'word')
        """
        svg_html = requests.get(svg_url, headers=self.headers).content.decode()
        word_list = re.findall(r'<textPath xlink:href="#(\d+)" textLength=".*?">(.*?)</textPath>', svg_html)
        svg_dic_w = [{'number': i[0], 'word': i[1]} for i in word_list]  # {'number': '', 'word:''}
        height_list = re.findall(r'<path id="(\d+)" d="M0 (\d+) H600"/>', svg_html)
        svg_dic_h = [{'number': i[0], 'height': i[1]} for i in height_list]  # {'number': '', 'height:''}
        n_h_w = [{**svg_dic_w[i], **svg_dic_h[i]} for i in
                 range(len(svg_dic_w))]  # {'number': '', 'word:'', 'height:''}
        h_w = [(int(i['height']), i['word']) for i in n_h_w]  # ('height': 'word')
        return h_w

    def dictionary(self, h_w, css_map):
        """
        把解析css与svg的结果合并得到加密的字典
        :return: dictionary {word: svg}
        """
        dictionary = []
        for i in css_map:
            try:
                for m in h_w:  # h = 1690
                    if int(m[0]) < int(i[2]):
                        pass
                    else:
                        line = int(i[1] / 14)
                        word = m[1][line]
                        item = {word: i[0]}
                        dictionary.append(item)
                        # print(item)
                        break
            except Exception as e:
                pass
        return dictionary


class DaZhong:
    def conversion(self, html, data):
        """
        解密svg
        :param data: 解析出来的对应表
        :param html: 未解密的html_str
        :return: 解密后的html
        """
        for i in data:
            for key, value in i.items():
                html = re.sub(r'<svgmtsi class="{}"></svgmtsi>'.format(value), key, html)
        return html

    def get_data(self, conversion_html):
        """
        得到名字，头像，项目评分，餐饮评分，划算评分，人均评分
        :param conversion_html:解密之后的html
        :return:数据的列表
        """
        data = []
        html = etree.HTML(conversion_html)
        try:
            next_page_url = 'http://www.dianping.com' + html.xpath('.//a[@class="NextPage"]/@href')[0]
        except IndexError:
            next_page_url = None
        li_list = html.xpath('//div[@class="reviews-items"]/ul/li')
        for li in li_list:
            item = {}
            try:
                item['name'] = li.xpath('.//div[@class="dper-info"]/a/text()')[0].replace(' ', '').replace('\n', '')
            except IndexError:
                item['name'] = li.xpath('.//div[@class="dper-info"]/span/text()')[0].replace(' ', '').replace('\n', '')
            item['head_portrait'] = li.xpath('.//*[@class="dper-photo-aside"]/img/@src')[0] if len(li.xpath('.//*[@class="dper-photo-aside"]/img/@src')) else None
            item['project_score'] = li.xpath('.//span[@class="score"]/span[1]/text()')[0].replace(' ', '').replace('\n', '') if len(li.xpath('.//span[@class="score"]/span[1]/text()')) else None
            item['food_score'] = li.xpath('.//span[@class="score"]/span[2]/text()')[0].replace(' ', '').replace('\n', '') if len(li.xpath('.//span[@class="score"]/span[2]/text()')) else None
            item['cost-effective_score'] = li.xpath('.//span[@class="score"]/span[3]/text()')[0].replace(' ', '').replace('\n', '') if len(li.xpath('.//span[@class="score"]/span[3]/text()')) > 0 else None
            item['capita_price_score'] = li.xpath('.//span[@class="score"]/span[4]/text()')[0].replace(' ', '').replace(
                '\n', '') if len(li.xpath('.//span[@class="score"]/span[4]/text()')) > 0 else None
            item['comment'] = ''.join(li.xpath('.//div[@class="review-words Hide"]/text()')).replace(' ', '').replace('\n', '').replace('\t', '')
        return next_page_url, data

    def save_data(self, data):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.spider
        collection = db.name
        collection.insert_many(data)


