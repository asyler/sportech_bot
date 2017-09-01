# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

from bookmakers.items import BookmakerOdd


class PaddypowerSpider(scrapy.Spider):
    name = 'paddypower'
    allowed_domains = ['paddypower.com']
    start_urls = ['http://www.paddypower.com/football/international-football/world-cup-2018?ev_oc_grp_ids=1828129']

    def parse(self, response):
        bets = response.css('span.odd > a')
        for bet in bets:
           country = bet.css('span.odds-label::text').extract_first().strip()
           odd = bet.css('span.odds-value::text').extract_first()
           yield BookmakerOdd(country=country, odd=odd)

