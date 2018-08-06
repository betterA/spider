import requests
import re
import json
from multiprocessing import Pool

def getHtml(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def getMovie(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".'
                        +'*?name"><a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime'
                        +'">(.*?)</p>.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
    items = re.findall(pattern, html)  
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5]+item[6] 
        }
def writefile(content):
    with open('movie.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = getHtml(url)
    for item in getMovie(html):
        writefile(item)

if __name__ == '__main__':
    pool = Pool()
    pool.map(main,[i*10 for i in range(10)])