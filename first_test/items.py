# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    site_name = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    short_desc = scrapy.Field()
    image = scrapy.Field()
    all_images = scrapy.Field()
    num = scrapy.Field()
    count_comment = scrapy.Field()
    stars = scrapy.Field()
