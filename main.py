# coding=utf-8
# @Time :  2021/1/26 13:11
# @Author : zjk
# @File : main.py
# @software : PyCharm

from dazhong import *


class SpiderDaZhong():
    def __init__(self, start_url, cookie):
        self.all_evaluate_url = start_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Cookie': cookie,
            'Host': 'www.dianping.com'
        }

    def parse(self, url):
        html = requests.get(url, headers=self.headers).text
        return html

    def analytical(self, html_str):
        ad = AnalyticalData()
        css_url = ad.css_url(html_str)
        svg_url = ad.svg_url(css_url)
        css_map = ad.get_css_dict(css_url)
        h_w = ad.get_svg_dict(svg_url)
        dictionary = ad.dictionary(h_w, css_map)
        return dictionary

    def data(self, html_str, dictionary):
        dz = DaZhong()
        conversion_html = dz.conversion(html_str, dictionary)
        next_page_url, data = dz.get_data(conversion_html)
        dz.save_data(data)

    def run(self):
        page = 1
        next_page_url = self.all_evaluate_url
        while next_page_url:
            html_str = self.parse(next_page_url)
            dictionary = self.analytical(html_str)
            self.data(html_str, dictionary)
            print('爬取完第{}页'.format(page))
            page += 1


if __name__ == '__main__':
    start_url = 'http://www.dianping.com/shop/k7Tg2oemgS7Gj10c/review_all'
    cookie = ''  # 写入cookie
    spider = SpiderDaZhong(start_url, cookie)
    spider.run()
