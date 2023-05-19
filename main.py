# -*- coding: utf-8 -*-
import time
import threading
import crawler_functions as cf


def main():
    proxy_list = cf.get_proxy_list()
    main_categories_list = cf.get_main_category_list()
    subcategories_list = cf.check_for_subcategories(main_categories_list, proxy_list)
    product_url_list = cf.get_product_page_url(subcategories_list, proxy_list)
    # product_url_list = ['https://www.gaslinespb.ru/catalog/elektricheskie_vodonagrevateli/thermex/mechanik/thermex_mk_100_v/']
    cf.save_product_info(product_url_list, proxy_list)
    #cf.save_product_image('https://www.gaslinespb.ru/catalog/elektricheskie_kotly/elektricheskiy_kotel_protherm_skat_12_kvt/', proxy_list, 111)


if __name__ == '__main__':
    main()
