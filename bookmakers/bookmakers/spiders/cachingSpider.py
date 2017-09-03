import json

from scrapy.spiders import CrawlSpider


class CachingSpider(CrawlSpider):
    def __init__(self, *args, **kwargs):
        self.cache = None
        try:
            with open(self.name,'r') as cache:
                cache_info = json.loads(cache.read())
                self.cache = cache_info
                self.start_urls = [self.cache['url']]
                if getattr(self, 'parse_item', None):
                    self.parse = self.parse_item
        except EnvironmentError:
            print('No cache found')

        super().__init__(*args, **kwargs)

    def save_to_cache(self, data):
        if not self.cache:
            try:
                print('Creating cache file')
                with open(self.name, 'w') as cache:
                    cache.write(json.dumps(data))
            except EnvironmentError:
                print("Can't create cahce file")


