# -*- coding: utf-8 -*-
from .bookmakerSpider import BookmakerSpider


class PaddypowerSpider(BookmakerSpider):
    name = 'paddypower'
    allowed_domains = ['paddypower.com']
    start_urls = ['http://www.paddypower.com/']