# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os


class BookmakersPipeline(object):
    def open_spider(self, spider):
        path = 'spider_results/'
        if not os.path.exists(path):
            os.makedirs(path)
        self.file = open(f'{path}/{spider.name}.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
