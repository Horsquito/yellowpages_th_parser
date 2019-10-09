import scrapy
from ..items import YellowpagesThParserItem
from datetime import datetime

class YellowpagesThParser(scrapy.Spider):
    name = "yellowpages_th_parser"

    def start_requests(self):
        url = 'https://www.yellowpages.co.th/ypsearch?q=' + str(self.product) + '&w='
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for href in response.xpath('//h3/a[@target="_blank"]/@href').getall():
            yield response.follow(href, self.parse_company_products)
        next_page = response.xpath('//ul[@class="pagination js-pager__items"]/li[@class="pager__item pager__item--next"]/a/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_company_products(self, response):
        item = YellowpagesThParserItem()
        if response.xpath('//h1[@class="notranslate"]/text()').get() is not None:
            name = response.xpath('//h1[@class="notranslate"]/text()').get()
            email_and_website = response.xpath('//div[@class="col-md-9 col-sm-8 col-xs-12 text-wrap padding-mobile"]/p/a/text()').getall()
            phone = response.xpath('//a[@class="telephone"]/@href').getall()
            contacts = email_and_website + phone
            if response.xpath('//div[@class="wg-content "]/ul/li/text()').getall() is not None:
                description = response.xpath('//div[@class="wg-content "]/ul/li/text()').getall()
            else:
                description = response.xpath('//div[@class="wg-content "]/p[@class="MsoNoSpacing"]/text()').getall()
        elif response.xpath('//h2[@class="typ-profile-title profile-title-color"]/text()').get() is not None:
            name = response.xpath('//h2[@class="typ-profile-title profile-title-color"]/text()').get()
            description = response.xpath('//div[@class="col-md-12 col-sm-12 col-xs-12 no-gutter profile-content profile-product-description"]/div/text()').getall()
            contacts = response.xpath('//div[@class="col-md-10 col-sm-10 col-xs-12 no-gutter contact-details"]/a/@href').getall()
        date_and_time = datetime.now().strftime('%d-%m %H:%M')
        item['name'] = name
        item['source'] = 'https://www.yellowpages.co.th'
        item['contacts'] = contacts
        item['product'] = self.product
        item['description'] = description
        item['hs_code'] = self.hs_code
        item['date_and_time'] = date_and_time
        yield item
