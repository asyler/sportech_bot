import json

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

from bookmakers.spiders.paddypower import PaddypowerSpider
from bookmakers.spiders.williamhill import WilliamhillSpider
from bookmakers.spiders.bet365 import Bet365Spider
from bookmakers.spiders.skybet import SkybetSpider

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

# spiders = [PaddypowerSpider, WilliamhillSpider, Bet365Spider, SkybetSpider]
spiders = [SkybetSpider]


# read docs
@defer.inlineCallbacks
def crawl():
    for spider in spiders:
        yield runner.crawl(spider)
    reactor.stop()

crawl()

reactor.run()

def collect_files():
    data = {}
    # use stats collector instead

    for spider in spiders:
        file = open(f'spider_results/{spider.name}.jl', 'r')
        lines = file.readlines()
        file.close()

        for line in lines:
            odd_data = json.loads(line)
            data.setdefault(odd_data['country'], [])
            data[odd_data['country']].append(odd_data['odd'])

    file = open('matrix.csv', 'w')

    bookmakers_str = ','.join(['']+[spider.name for spider in spiders])
    file.write(bookmakers_str+'\n')

    for country, odds in data.items():
        file.write(','.join([country]+odds)+'\n')


collect_files()