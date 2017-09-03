# -*- coding: utf-8 -*-
from bookmakers.items import BookmakerOdd
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider


class PaddypowerSpider(CrawlSpider):
    name = 'paddypower'
    allowed_domains = ['paddypower.com', 'sports.williamhill.com']
    # start_urls = ['http://www.paddypower.com/football/international-football/world-cup-2018?ev_oc_grp_ids=1828129']
    start_urls = ['http://www.paddypower.com/']
    # start_urls = ['http://sports.williamhill.com/bet/en-gb']

    rules = (
        Rule(
            LinkExtractor(
                restrict_xpaths=(
                    '//a[contains(.,"World Cup 2018")]',
                    '//a[contains(.,"All")]',
                    '//a[contains(.,"Outright")]',
                    '//a[contains(.,"Football")]',
                )
            ),
            callback='parse_item', follow=True
        ),
    )

    def parse_item(self, response):
        wc = response.xpath('//*[not(self::script)][contains(text(),"World Cup 2018")]')
        country_1 = response.xpath('//*[not(self::script)][contains(text(),"Ukraine")]')
        country_2 = response.xpath('//*[not(self::script)][contains(text(),"Northern Ireland")]')

        if wc and country_1 and country_2:
            print(response.url,1)
            el = {
                'name': country_1.xpath('name()').extract()[0],
                'class_': ', '.join(country_1.xpath('@class').extract())
            }
            country_label_xpath = '//{}[@class="{}"]'.format(el['name'], el['class_'])
            odds_xpath = '{}/../{}[re:match(text(),"\d")]'.format(country_label_xpath, el['name'])

            country_labels = response.xpath(country_label_xpath+'/text()').extract()
            odds = response.xpath(odds_xpath+'/text()').extract()

            for country, odd in zip(country_labels, odds):
               yield BookmakerOdd(country=country, odd=odd)

            raise CloseSpider('odds found')
