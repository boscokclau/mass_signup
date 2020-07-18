#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 17, 2020

@author: boscolau
"""

import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def get_active_events(organizer_url: str, headless=True) -> list:
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    driver.get(organizer_url)

    event_divs = driver.find_elements_by_xpath("//article[@id='live_events']/div[contains(@class,'list-card-v2')]")

    event_list = list()
    for event_div in event_divs:
        event_name = event_div.get_attribute('data-share-name')
        event_a = event_div.find_element_by_xpath("./a")
        event_url = event_a.get_attribute('href')

        an_event = dict()
        an_event['event_name'] = event_name
        an_event['event_url'] = event_url
        event_list.append(an_event)

    return event_list

if __name__ == "__main__":
    events = get_active_events("https://giowoods.eventbrite.com", headless=True)
    print(str(events))
