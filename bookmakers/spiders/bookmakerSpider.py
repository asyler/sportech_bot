# -*- coding: utf-8 -*-
import difflib

from scrapy import Request
from scrapy.exceptions import CloseSpider

from bookmakers.items import BookmakerOdd
from .cachingSpider import CachingSpider


class BookmakerSpider(CachingSpider):
    def get_all_html_elements(self, response):
        elements = response.xpath('//*[not(self::script)]')
        return [(el.xpath('text()').extract_first(), el, el.xpath('ancestor-or-self::*[@href]')) for el in elements if
                el.xpath('text()')]

    def find_countries_elements(self):
        country_elements = {}
        for element_text, element, link in self.all_elements:
            for country in self.countries:
                if country in element_text:
                    country_elements.setdefault(country, [])
                    country_elements[country].append(element)
        return country_elements

    def check_page_contains_countries(self):
        return len(self.country_elements.keys()) / len(self.countries) > self.confidences['number_of_countries']

    def find_odd(self, country, country_elements):
        texts = [el.xpath('text()').extract_first().strip() for el in country_elements]
        best_match = difflib.get_close_matches(country, texts, 1, self.confidences['country_name'])
        match_elements = [country_elements[i] for i, text in enumerate(texts) if text==best_match[0]]
        for el in match_elements:
            yield el.xpath('ancestor-or-self::*')[::-1].re_first('\d+/\d+')

    def match_all_keywords(self, url):
        all_texts = [el[0] for el in self.all_elements]
        for keywords in self.market_keywords:
            avg_matches = 0
            for keyword in keywords:
                avg_matches += len(difflib.get_close_matches(keyword, all_texts, len(all_texts), self.confidences['market_name']))\
                               +len([text for text in all_texts if keyword in text])
            if avg_matches == 0:
                return False
        return True

    def parse(self, response):
        self.all_elements = self.get_all_html_elements(response)
        self.country_elements = self.find_countries_elements()
        if self.check_page_contains_countries() and self.match_all_keywords(response.url):
            for country, elements in self.country_elements.items():
                odds = self.find_odd(country, elements)
                for odd in odds:
                    yield BookmakerOdd(country=country, odd=odd)

            self.save_to_cache({
                'url': response.url
            })

            raise CloseSpider('odds found')
        else:
            links_elements = [(el[0], el[1], el[2].xpath('@href').extract_first()) for el in self.all_elements
                              if len(el[2])]
            links_texts = [el[0] for el in links_elements]
            for keywords in self.market_keywords:
                for keyword in keywords:
                    links = [link for link in links_texts if keyword in link]
                    for link in links:
                        request = Request(response.urljoin(links_elements[links_texts.index(link)][2]))
                        yield request
