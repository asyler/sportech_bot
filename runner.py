import json
import logging
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from bookmakers.spiders.bet365 import Bet365Spider
from bookmakers.spiders.paddypower import PaddypowerSpider
from bookmakers.spiders.skybet import SkybetSpider
from bookmakers.spiders.williamhill import WilliamhillSpider

settings = get_project_settings()
spiders = [PaddypowerSpider, SkybetSpider, WilliamhillSpider, Bet365Spider]
logger = logging.getLogger()


def collect_files():
    logger.warning('producing final file')
    data = {}

    for i, spider in enumerate(spiders):
        with open(f'spider_results/{spider.name}.jl', 'r') as file:
            lines = file.readlines()

        for line in lines:
            odd_data = json.loads(line)
            data.setdefault(odd_data['country'], [''] * len(spiders))
            data[odd_data['country']][i] = odd_data['odd']

    with open('matrix.csv', 'w') as file:

        bookmakers_str = ','.join([''] + [spider.name for spider in spiders])
        file.write(bookmakers_str + '\n')

        for country, odds in data.items():
            file.write(','.join([country] + odds) + '\n')


def main():
    logger.warning('starting...')

    proxy = os.getenv('https_proxy', None)
    if proxy:
        logger.warning(f'proxy found: {proxy}')
    else:
        logger.warning('proxy not found')

    process = CrawlerProcess(settings)
    for spider in spiders:
        process.crawl(spider)
    process.start()
    collect_files()
    logger.warning('finished!')


if __name__ == '__main__':
    main()
