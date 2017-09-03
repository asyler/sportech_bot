# -*- coding: utf-8 -*-
import os

from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

from bookmakers.items import BookmakerOdd
from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

from .cachingSpider import CachingSpider


class BookmakerSpider(CachingSpider):
    need_proxy = False

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

    def __init__(self):
        print (os.getenv('https_proxy'))
        os.unsetenv('https_proxy')

        super().__init__()

    def get_odds_xpath(self, country):
            if self.cache:
                return self.cache['country_label_xpath'], self.cache['odds_xpath']

            el = {
                'name': country.xpath('name()').extract()[0],
                'class_': ', '.join(country.xpath('@class').extract())
            }
            country_label_xpath = '//{}[@class="{}"]'.format(el['name'], el['class_'])
            odds_xpath = '{}/../*[not(self::script)][re:match(text(),"\d")]'.format(country_label_xpath)

            return country_label_xpath, odds_xpath

    def parse_item(self, response):
            wc = response.xpath('//*[not(self::script)][contains(text(),"World Cup 2018")]')
            country_1 = response.xpath('//*[not(self::script)][contains(text(),"Ghana")]')
            country_2 = response.xpath('//*[not(self::script)][contains(text(),"Northern Ireland")]')

            if wc and country_1 and country_2:
                country_label_xpath, odds_xpath = self.get_odds_xpath(country_1)

                country_labels = response.xpath(country_label_xpath+'/text()').extract()
                odds = response.xpath(odds_xpath+'/text()').extract()

                for country, odd in zip(country_labels, odds):
                   yield BookmakerOdd(country=country.strip(), odd=odd.strip())

                self.save_to_cache({
                    'url':response.url,
                    'country_label_xpath': country_label_xpath,
                    'odds_xpath': odds_xpath,
                })

                raise CloseSpider('odds found')
