# -*- coding: utf-8 -*-
import time

import re
from bookmakers.items import BookmakerOdd
from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

MAX_WAIT = 5

def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.1)
    return modified_fn

@wait
def wait_for(fn):
    return fn()

class Bet365Spider(Spider):
    name = 'bet365'
    allowed_domains = ['mobile.bet365.com']
    start_urls = ['https://mobile.bet365.com']

    def __init__(self):
        self.browser = webdriver.Firefox()

        self.odd_pattern = re.compile(r"^\d")

    def closed(self, reason):
        self.browser.quit()

    @wait
    def wait_for(self, xpath):
        return wait_for(lambda: self.browser.find_element(By.XPATH, xpath))

    def parse(self, response):
        self.browser.get(response.url)
        wait_for(lambda: self.browser.find_element_by_id('SplashContent')) # wait for load

        link1 = self.wait_for('//*[not(self::script)][contains(text(),"Soccer")]')
        link1.click()

        link2 = self.wait_for('//*[not(self::script)][contains(text(),"Outrights")]')
        link2.click()

        link3 = self.wait_for('//*[not(self::script)][contains(text(),"World Cup 2018")]')
        link3.click()

        wait_for(lambda: self.browser.find_element_by_id('Coupon'))

        country_1 = self.browser.find_element(By.XPATH, '//*[not(self::script)][contains(text(),"Northern Ireland")]')

        el = {
            'name': country_1.tag_name,
            'class_': country_1.get_attribute('class')
        }
        country_label_xpath = '//{}[@class="{}"]'.format(el['name'], el['class_'])

        country_labels = self.browser.find_elements(By.XPATH, country_label_xpath)

        for country in country_labels:
            parent_el = country.find_element(By.XPATH, '..')
            country_labels_children = country.find_elements_by_xpath(".//*")
            total_text_len = country.text
            for child in children:
                to
            odds_candidates = parent_el.find_elements_by_tag_name(el['name'])
            for candidate in odds_candidates:
                match = self.odd_pattern.match(candidate.text)
                if match:
                    odd = candidate
                    yield BookmakerOdd(country=country_text.strip(), odd=odd.text.strip())
                    break

        raise CloseSpider('odds found')
