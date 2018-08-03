import os
from hashlib import md5

import requests
from urllib.parse import urlencode
from multiprocessing import Pool


def get_page(offset):
    base_url = 'https://www.toutiao.com/search_content/?'
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    url = base_url + urlencode(params)

    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def parse_page(json):
    items = json.get('data')
    for item in items:
        title = item.get('title')
        images = item.get('image_list')
        if images:
            data = {}
            for image in images:
                image = 'http:' + image['url']
                data['title'] = title
                data['image'] = image
                yield data


def save_images(item):
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    try:
        local_image_url = item.get('image')
        ''' 将'list'替换成'origin'是因为‘http://p1.pstatp.com/list/pgc-image/1529664103590c0c5740383’的结果是小图，
        在头条打开图片链接观察到‘http://p1.pstatp.com/origin/pgc-image/1529664103590c0c5740383’打开的才是高清大图'''
        new_image_url = local_image_url.replace('list', 'origin')
        response = requests.get(new_image_url)
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                print('文件名存在')
    except requests.ConnectionError:
        print('图片保存失败')


def main(offset):
    json = get_page(offset)
    results = parse_page(json)
    for result in results:
        print(result)
        save_images(result)


if __name__ == '__main__':
    '''进程池加快爬取'''
    pool = Pool()
    groups = ([x * 20 for x in range(0, 8)])
    pool.map(main, groups)
    pool.close()
    pool.join()

