from urllib import quote
import re
import scrapy
from first_test.items import ProductItem


class RozetkaSpider(scrapy.Spider):
    name = "rozetka"
    allowed_domains = ["rozetka.com.ua"]
    SEARCH_URL = ("http://rozetka.com.ua/search/scroll=true;text={search_term};"
                  "section=%2F;search-button=;p={quantity}/")

    def __init__(self, quantity=None, search_term=None, **kwargs):
        super(RozetkaSpider, self).__init__(**kwargs)
        self.quantity = int(quantity)
        self.search_term = search_term
        self.cur_page = 0

    def next_page_request(self, cur_num=0):
        url = self.SEARCH_URL.format(quantity=self.cur_page,
                                     search_term=quote(self.search_term))
        self.cur_page += 1
        return scrapy.Request(url, callback=self.parse, meta={'cur_num':cur_num})

    def start_requests(self):
        return [self.next_page_request()]

    def parse_details(self, response):
        cur_item = response.meta.get('cur_item')
        all_images_tmp = response.xpath('//div[@class="detail-img-thumbs-l"]/div/a/@data-accord-original-url').extract()
        cur_item['all_images'] = all_images_tmp
        return cur_item

    def parse(self, response):
        prods = response.css('.g-i-list')
        if not prods:
            return
        i = 0
        for i, prod in enumerate(prods, start=response.meta.get('cur_num')):
            if i >= self.quantity:
                return
            item = ProductItem()
            item['name'] = prod.xpath('.//div[@class="g-i-list-title"]/a/text()')[0].extract()
            item['link'] = prod.xpath('.//div[@class="g-i-list-title"]/a/@href')[0].extract()

            item['image'] = prod.xpath('.//div[@class="g-i-list-img"]/a/img/@data_src')[0].extract()
            price = prod.xpath('.//div[@name="price"]/div[@class="g-price-uah"]/text()')
            if price:
                item['price'] = price[0].extract()
            desc = prod.xpath('.//div[@class="g-i-list-description"]/text()')
            if desc:
                item['short_desc'] = desc[0].extract()
            item['num'] = i
            comments = prod.xpath('.//span[@class="g-rating-reviews"]/text()').re(r'\d+')
            if comments:
                item['count_comment'] = int(comments[0])
                stars = prod.xpath('.//span[contains(@class,"g-rating-stars-i")]/@style').re(r'width:(\d+)')
                if stars:
                    item['stars'] = int(stars[0]) / 20
            if item['link']:
                yield scrapy.Request(item['link'], callback=self.parse_details, meta={
                    'cur_item': item})
        yield self.next_page_request(i+1)
