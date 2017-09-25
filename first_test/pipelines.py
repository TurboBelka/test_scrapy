# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from urllib import quote
from scrapy.exceptions import DropItem


class PricePipeline(object):

    def process_item(self, item, spider):
        tmp = item.get('price')
        if tmp:
            price = tmp.replace(u'\u2009', '')
            item['price'] = float(price)
        return item


class SiteNamePipeline(object):

    def process_item(self, item, spider):
        item['site_name'] = spider.allowed_domains[0]
        return item
