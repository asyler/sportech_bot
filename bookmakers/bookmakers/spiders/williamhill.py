# -*- coding: utf-8 -*-
from .bookmakerSpider import BookmakerSpider


class WilliamhillSpider(BookmakerSpider):
    name = 'williamhill'
    allowed_domains = ['sports.williamhill.com']
    start_urls = ['http://sports.williamhill.com']
