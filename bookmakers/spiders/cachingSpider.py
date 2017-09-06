import json

from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider


class CachingSpider(Spider):
    def __init__(self, *args, **kwargs):
        self.cache = None
        try:
            with open(f'spider_results/{self.name}_cache.json', 'r') as cache:
                cache_info = json.loads(cache.read())
                self._log('cache found')
                self.cache = cache_info
                self.start_urls = [self.cache['url']]
                if getattr(self, 'parse_item', None):
                    self.parse = self.parse_item
        except EnvironmentError:
            self._log('no cache found')

        try:
            with open('settings/countries.json') as file:
                self.countries = json.loads(file.read())
            with open('settings/confidences.json') as file:
                self.confidences = json.loads(file.read())
            with open('settings/market.json') as file:
                self.market_keywords = json.loads(file.read())
        except EnvironmentError:
            raise CloseSpider("can't load settings")

        super().__init__(*args, **kwargs)

    def _log(self, message):
        self.logger.warning(f'{self.name}: {message}')

    def save_to_cache(self, data):
        if not self.cache:
            try:
                self._log('creating cache file')
                with open(f'spider_results/{self.name}_cache.json', 'w') as cache:
                    cache.write(json.dumps(data))
            except EnvironmentError:
                self._log("can't create cache file")
