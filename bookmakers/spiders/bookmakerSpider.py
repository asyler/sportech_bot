# -*- coding: utf-8 -*-
import difflib

from scrapy.exceptions import CloseSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from bookmakers.items import BookmakerOdd
from .cachingSpider import CachingSpider


class BookmakerSpider(CachingSpider):
    def get_all_html_elements(self, response):
        elements = response.xpath('//*[not(self::script)]')
        return [(el.xpath('text()').extract_first(), el) for el in elements if
                el.xpath('text()')]

    def find_countries_elements(self):
        country_elements = {}
        for element_text, element in self.all_elements:
            for country in self.countries:
                if country in element_text:
                    country_elements.setdefault(country, [])
                    country_elements[country].append(element)
        return country_elements

    def check_page_contains_countries(self):
        return len(self.country_elements.keys())>self.confidences['number_of_countries']

    def find_odd(self, country, country_elements):
        texts = [el.xpath('text()').extract_first() for el in country_elements]
        bets_match = difflib.get_close_matches(country, texts, 1)[0]
        country_element = country_elements[texts.index(bets_match)]
        return country_element.xpath('ancestor-or-self::*')[::-1].re_first('\d+/\d+')

    def parse(self, response):
        self.all_elements = self.get_all_html_elements(response)
        self.country_elements = self.find_countries_elements()

        if self.check_page_contains_countries():
            for country, elements in self.country_elements.items():
                yield BookmakerOdd(country=country, odd=self.find_odd(country, elements))

            raise CloseSpider('odds found')
