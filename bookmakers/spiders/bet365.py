# -*- coding: utf-8 -*-
import re
import time

from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.by import By

from bookmakers.items import BookmakerOdd

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.2)

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

        super().__init__()

    def closed(self, reason):
        self.browser.quit()

    @wait
    def wait_for(self, xpath):
        return wait_for(lambda: self.browser.find_element(By.XPATH, xpath))

    def parse(self, response):

        try:
            self.browser.get(response.url)
            wait_for(lambda: self.browser.find_element_by_id('IconContainer'))  # wait for load

            link1 = self.wait_for('//*[not(self::script)][contains(text(),"Soccer")]')
            link1.click()

            wait_for(lambda: self.browser.find_element_by_id('overlay'))
            link2 = self.wait_for('//*[not(self::script)][contains(text(),"Outrights")]')
            link2.click()

            link3 = self.wait_for('//*[not(self::script)][contains(text(),"World Cup 2018")]')
            link3.click()

            wait_for(lambda: self.browser.find_element_by_id('Coupon'))
        except (ElementNotInteractableException, WebDriverException, NoSuchElementException):
            self.logger.warning(f'{self.name}: World Cup 2018 market not found')

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
            total_text_len = len(country.text)
            for child in country_labels_children:
                total_text_len -= len(child.text)
            odds_candidates = parent_el.find_elements_by_tag_name(el['name'])
            for candidate in odds_candidates:
                match = self.odd_pattern.match(candidate.text)
                if match:
                    odd = candidate
                    yield BookmakerOdd(country=country.text[:total_text_len].strip(), odd=odd.text.strip())
                    break

        raise CloseSpider('odds found')
