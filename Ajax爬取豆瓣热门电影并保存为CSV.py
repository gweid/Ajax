import time

import pandas
import requests
from multiprocessing import Pool
from urllib.parse import urlencode


def get_page(page_start):
    headers = {
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/explore',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/67.0.3396.87 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    base_url = 'https://movie.douban.com/j/search_subjects?'
    params = {
        'type': 'movie',
        'tag': '热门',
        'sort': 'recommend',
        'page_limit': '20',
        'page_start': page_start
    }
    url = base_url + urlencode(params)

    response = requests.get(url, headers=headers)
    try:
        if response.status_code == 200:
            return response.json()
    except requests.ConnectTimeout:
        return None


def parse_page(json):
    items = json.get('subjects')
    for item in items:
        score = item['rate']
        title = item['title']
        url = item['url']
        yield {
            '电影名': title,
            '评分': score,
            '豆瓣网址': url
        }


def save_csv(item):
    save = pandas.DataFrame(item)
    save.to_csv('豆瓣热门电影.csv', index=False, encoding='utf_8_sig', mode='a', header=False)


def main(page_start):
    json = get_page(page_start)
    items = parse_page(json)
    print(items)
    save_csv(items)


if __name__ == '__main__':
    pool = Pool()
    groups = [x * 20 for x in range(7)]
    pool.map(main, groups)
    time.sleep(1)  # 加个时间延迟是为了防止豆瓣的反爬
    pool.close()
    pool.join()
