from urllib import quote
import scrapy
from first_test.items import ProductItem


class OkSpider(scrapy.Spider):
    name = "ok_site"
    allowed_domains = ["5ok.com.ua"]
    SEARCH_URL = "http://www.5ok.com.ua/search.html?text={search_term}&page={page}"

    def __init__(self, quantity=None, search_term=None, **kwargs):
        super(OkSpider, self).__init__(**kwargs)
        self.quantity = int(quantity)
        self.search_term = search_term
        self.cur_page = 1

    def next_page_request(self, cur_num=0):
        url = self.SEARCH_URL.format(search_term=quote(self.search_term),
                                     page=self.cur_page)
        self.cur_page += 1
        return scrapy.Request(url, callback=self.parse,
                              meta={'cur_num': cur_num})

    def start_requests(self):
        return [self.next_page_request()]

    def parse_details(self, response):
        cur_item = response.meta.get('cur_item')
        all_images = response.xpath(
            './/div[@class="img"]/div//img/@src').extract()
        all_images = map(lambda x: 'http://www.%s%s' % (self.allowed_domains[0], x), all_images)
        # for image in all_images:
        #     url_tmp = "http://www.%s%s" % (self.allowed_domains[0], image)
        #     cur_item['all_images'] = url_tmp
        cur_item['all_images'] = all_images
        return cur_item

    def parse(self, response):
        all_prods = response.css('.gtile-i-box')
        i = 1
        for i, prod in enumerate(all_prods, start=response.meta.get('cur_num')):
            if i >= self.quantity:
                return
            item = ProductItem()
            item['name'] = prod.xpath('.//div[@class="title"]/h5/a'
                                      '/text()')[0].extract()
            item['link'] = "http://www.%s%s" % (self.allowed_domains[0], prod.xpath('.//div[@class="title"]/h5/a'
                                      '/@href')[0].extract())
            item['image'] = prod.xpath('.//div[@class="img-border"]/a[@class="img"]'
                       '/img/@data-original')[0].extract()
            item['price'] = prod.xpath('.//div[@class="left-block"]'
                                             '/span[@class="product-price"]'
                                             '/text()')[0].extract()
            item['short_desc'] = ''.join(prod.xpath('.//div[@class="text"]'
                                            '/span[@id="lblDescription"]'
                                            '/a//text()').extract())
            count_comment = prod.xpath('.//div[@class="block_stars"]'
                                       '/a/text()').re(r'\d+')
            if count_comment:
                item['count_comment'] = int(count_comment[0])
                stars = prod.xpath('.//div[@class="block_stars"]'
                                   '/span[not(contains(@class, "empty"))]'
                                   '[contains(@class, "star")]').extract()
                item['stars'] = len(stars)
            item['num'] = i
            if item['link']:
                yield scrapy.Request(item['link'], callback=self.parse_details,
                                     meta={
                                         'cur_item': item})
        yield self.next_page_request(i + 1)
