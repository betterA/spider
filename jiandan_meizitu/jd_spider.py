import base64
import requests
from bs4 import BeautifulSoup
import re
import os
from multiprocessing import Pool


def _base64_decode(data):
    '''base64解码,要注意字符长度'''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)


def get_img_url(m: str) -> str:
    '''通过image-hash解码 返回url
    :param m:str  image-hash
    :return :str  img_url
    '''
    t = _base64_decode(m)
    t = 'http:' + t.decode("utf-8")
    t = re.sub('mw\d*', 'large', t)
    return t


def get_page(url, pic=False):
    '''获取页面
    :param url:str url
    :param pic:bool is picture url
    :return   :pic = False  r.text or None
    :         :pic = True   r.content or None
    '''
    headers = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text if not pic else r.content
        return None
    except ConnectionError:
        return None


def parse_img_url(html: str) ->str:
    """分析html
    :param html:str  html-text
    :yield     :str  img-hash 
    """
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.select('.img-hash')
    for tag in tags:
        yield tag.text


def download_img(url):
    print("正在下载", url)
    context = get_page(url, pic=True)
    if context:
        save_image(url, context)


def save_image(url, content):
    name = url.split('/')[-1]
    file_path = f"{os.getcwd()}/img/{name}"
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def main(page):
    url = f'http://jandan.net/ooxx/page-{page}#comments'
    html = get_page(url)
    if html:
        for i in parse_img_url(html):
            t = get_img_url(i)
            download_img(t)


if __name__ == '__main__':
    page = [38-i for i in range(38)]
    pool = Pool()
    pool.map(main, page)
