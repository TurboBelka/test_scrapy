from urllib import quote
import urllib
import urlparse
import scrapy


class YandexSpider(scrapy.Spider):
    name = "yandex"
    allowed_domains = ["market.yandex.ua"]
    SEARCH_URL ="https://market.yandex.ua/search.xml?cvredirect=2&text={search_term}"

    def __init__(self, quantity=None, search_term=None, **kwargs):
        super(YandexSpider, self).__init__(**kwargs)
        self.quantity = int(quantity)
        self.search_term = search_term
        self.cur_page = 1

    def start_requests(self):
        url = self.SEARCH_URL.format(search_term=quote(self.search_term))
        return [scrapy.Request(url, callback=self.parse)]

    def next_page_request(self, url, cur_num=0):
        url_tmp = urlparse.urlparse(url)
        params_url = urlparse.parse_qs(url_tmp.query)
        params_url['page'] = str(int(params_url.get('page', '0')) + 1)
        url_tmp = url_tmp._replace(query=urllib.urlencode(params_url))
        new_url = urlparse.urlunparse(url_tmp)

        return scrapy.Request(new_url, callback=self.parse_all_models, meta={'cur_num':cur_num})

    def parse_all_models(self, response):
        all_prods = response.css('.snippet-list > .snippet-card').extract()
        if not all_prods:
            return

        for prod in all_prods:
            yield prod

    def parse(self, response):
        all_models = response.css('.top-3-models__title-link::attr(href)').extract()
        if all_models:
            self.next_page_request(all_models[0])
