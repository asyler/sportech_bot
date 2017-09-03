# -*- coding: utf-8 -*-
from scrapy import Spider, Request

from .bookmakerSpider import BookmakerSpider


class SkybetSpider(BookmakerSpider):
    name = 'skybet'
    allowed_domains = ['skybet.com']
    start_urls = ['https://www.skybet.com/']

    need_proxy = True