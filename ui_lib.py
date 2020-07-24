#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jul 17, 2020

@author: boscolau
"""

import logging
from pubsub import pub
from constants import EventTopic
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def get_active_events(organizer_url: str, headless=True) -> list:
    event_list = list()

    try:
        options = Options()
        options.headless = headless
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        driver.get(organizer_url)

        event_divs = driver.find_elements_by_xpath("//article[@id='live_events']/div[contains(@class,'list-card-v2')]")

        for event_div in event_divs:
            event_name = event_div.get_attribute('data-share-name')
            event_a = event_div.find_element_by_xpath("./a")
            event_url = event_a.get_attribute('href')

            an_event = dict()
            an_event['event_name'] = event_name
            an_event['event_url'] = event_url
            event_list.append(an_event)
    finally:
        driver.quit()

    return event_list


def display_progress_message(msg: str):
    logger = logging.getLogger(EventTopic.DISPLAY_PROGRESS_MESSAGE)
    logger.info(msg)
    pub.sendMessage(EventTopic.DISPLAY_PROGRESS_MESSAGE, msg=msg)

def process_order_summary(info_dict: dict):
    pub.sendMessage(EventTopic.DISPLAY_ORDER_SUMMARY, info_dict=info_dict)


if __name__ == "__main__":
    events = get_active_events("https://giowoods.eventbrite.com", headless=True)
    print(str(events))
