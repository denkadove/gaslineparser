import os
import random
from bs4 import BeautifulSoup
import requests
import httplib2
import re


def get_proxy_list():
    """
    get proxy list from 'proxy.txt'
    :return: proxy_list
    """
    f = open('proxy.txt', 'r')
    proxy_list = f.readlines()
    proxy_list = [line.rstrip() for line in proxy_list]
    f.close()
    return proxy_list


def get_single_proxy(proxy_list):
    """
    function select random proxy from list and check it
    :param proxy_list:
    :return: single_proxy
    """
    proxy = proxy_list[random.randint(0, len(proxy_list) - 1)]
    p = {"http": proxy}
    url = 'https://yandex.ru'
    response = requests.get(url, proxies=p, timeout=5, headers={
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) '
                      'Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    # print(response.status_code)
    if response.status_code == 200:
        # print(proxy, '=> 200 OK')
        return p
    else:
        get_single_proxy(proxy_list)


def get_main_category_list():
    """
    get main categories list from file "main_categories.txt"
    :return: "main_categories_url_list" - list of main categories
    """
    print('Получаем ссписок категорий для анализа... ', end='')
    f = open('main_categories.txt')
    main_categories_url_list = f.readlines()
    main_categories_url_list = [line.rstrip() for line in main_categories_url_list]
    f.close()
    return main_categories_url_list


def check_for_subcategories(main_categories_list, proxy_list):
    """
    check all links in main categories list and
    try to find subcategories
    :param main_categories_list:
    :param proxy_list:
    :return: subcategories_list
    """
    print('Собираем ссылки на подкатегории... ', end='')
    subcategories_list = main_categories_list
    for url in main_categories_list:
        p = get_single_proxy(proxy_list)
        response = requests.get(url, proxies=p, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) '
                          'Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'identity'})
        soup = BeautifulSoup(response.text, 'html.parser')
        link_list = soup.select("div.info > div.title > a")
        pagination_list = soup.select("ul.pagination > li.next > a")

        if len(pagination_list) != 0:
            for pagination_item in pagination_list:
                subcategories_list.append('https://www.gaslinespb.ru' + pagination_item.get('href'))

        if len(link_list) != 0:
            for cat_link in link_list:
                if ('https://www.gaslinespb.ru' + cat_link.get('href')) not in subcategories_list:
                    subcategories_list.append('https://www.gaslinespb.ru' + cat_link.get('href'))
                else:
                    subcategories_list.append(url)
    return subcategories_list


def get_product_page_url(subcategories_list, proxy_list):
    """
    get list of subcategories and return product pages list
    :param subcategories_list:
    :param proxy_list:
    :return: product_pages_list
    """
    print('Собираем ссылки на товары... ', end='')
    product_url_list = []
    for url in subcategories_list:
        p = get_single_proxy(proxy_list)
        response = requests.get(url, proxies=p, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) '
                          'Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
        soup = BeautifulSoup(response.text, 'html.parser')
        link_list = soup.select("div.text > div.cont > div > a")
        for product_link in link_list:
            product_url_list.append('https://www.gaslinespb.ru' + product_link.get('href'))
    print(len(product_url_list))
    return product_url_list


def save_product_image(url, proxy_list, product_id):
    """
    find product image snd save it on local disk
    :param product_id:
    :param url: product url
    :param proxy_list:
    :return:
    """
    p = get_single_proxy(proxy_list)
    response = requests.get(url, proxies=p, timeout=5, headers={
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) '
                      'Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    soup = BeautifulSoup(response.text, 'html.parser')
    # img_urls = soup.find('div', class_='flex-viewport')
    # img_urls = soup.find_all(itemprop='image')
    img_urls = soup.find('a', class_="fancybox blink")
    if img_urls is None:
        print(url + ' => image not found!!!')
    else:
        img_urls = soup.find_all('a', class_="fancybox blink")
        i = 1
        for img_url in img_urls:
            # img_urls = soup.select("fancybox blink")
            # print(img_urls)
            img_url = 'https://www.gaslinespb.ru/' + str(img_url.get('href'))
            h = httplib2.Http('.cache')
            response, content = h.request(img_url)
            out = open('images/' + str(product_id) + '(' + str(i) + ').jpg', 'wb')
            out.write(content)
            out.close()
            i += 1


def save_product_info(product_url_list, proxy_list):
    product_library = []
    product_id = 2963
    for url in product_url_list:
        p = get_single_proxy(proxy_list)
        response = requests.get(url, proxies=p, timeout=5, headers={
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5) '
                          'Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
        soup = BeautifulSoup(response.text, 'html.parser')
        product_name = soup.find("h1").text

        search_product_price = soup.find('span', class_='price_val')
        if search_product_price is None:
            search_product_price = soup.find(itemprop='price')
            if search_product_price is None:
                search_product_price = 'no price'
            else:
                search_product_price = soup.select('span.price_val > span:nth-child(1)')[0].text
        else:
            search_product_price = soup.select('span.price_val')[0].text
        product_price = search_product_price

        search_product_short_description = soup.find('div', class_='previewtext')
        if search_product_short_description is None:
            product_short_description = 'no full description'
        else:
            product_short_description = soup.select("div.previewtext")[0].text

        search_product_full_description = soup.find('div', class_='content')
        if search_product_full_description is None:
            product_full_description = 'no full description'
        else:
            product_full_description = soup.select("div.content")[0].text

        # new_string = str(url) + '~' + str(product_id) + '~' + str(product_id) + '~' + str(product_price)
        # product_library.append(new_string)
        # f = open('products.txt', 'a', encoding='utf-8')
        product_name = re.sub(r"[#%!@*/]", '-', str(product_name))
        new_string = product_name.replace('/', '-') + '\n' + str(product_short_description) + '\n' + str(product_full_description) + '\n'
        f = open('desc/' + str(product_id) + '-' + str(product_name) + '.txt', 'a', encoding='utf-8')
        f.write(new_string + '\n')
        f.close()
        f.close()
        # save_product_image(url, proxy_list, product_id)
        product_id += 1
