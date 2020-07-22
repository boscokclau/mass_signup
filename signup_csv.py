#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import argparse
import csv
import logging.config
import yaml
import mass_signup
import mass_signup_lib
from pubsub import pub
from constants import EventTopic, RegistrationStatus
import constants
from buyer import Buyer


def process_registration(event_url: str, csv_path: str, buyer_path: str, headless: bool = False,
                         process_all_by: int = 0):
    # Buyer is always the OLMV Mass EB organizer
    buyer_firstname = None
    buyer_lastname = None
    buyer_email = None

    with open(buyer_path, 'r') as f:
        buyer_firstname, buyer_lastname, buyer_email = next(csv.reader(f))

    buyer = Buyer(buyer_firstname, buyer_lastname, buyer_email)

    attendee_list_collection = mass_signup_lib.get_attendees_from_csv(csv_path, process_all_by)

    print("Processing {} order{}:".format(len(attendee_list_collection),
                                          "" if len(attendee_list_collection) == 1 else "s"))
    print("\tAttendee file:", csv_path)
    print("\tEvent: ", event_url)
    print()

    status_all = 0
    for i, attendee_list in enumerate(attendee_list_collection):
        print("Order:", i + 1)
        status, info_dict = mass_signup.signup(attendee_list, buyer, event_url, headless)
        print("status, order_id: ", status, ",", str(info_dict))

    # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
    if status != RegistrationStatus.COMPLETED:
        status_all = status_all | 1 << i

    return status_all


# Progress messages subscription and print()
def print_progress(msg: str):
    print("Progress Message:", msg)


pub.subscribe(print_progress, EventTopic.PROGRESS)

# Program Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('event_url', help='URL of the EventBrite event.')
    parser.add_argument('csv_path', help='File path to the attendee CSV file.')
    parser.add_argument('buyer_path', help='File path to the buyer csv file.')
    parser.add_argument('-c', '--command-line-mode', dest='headless', help='Command line mode. Run browser headless.',
                        action='store_true')
    parser.add_argument('-a', '-all_by', dest='process_all_by', default=0, help=argparse.SUPPRESS)
    parser.add_argument('-l', '-loglevel', dest='log_level',
                        choices=['critical', 'error', 'warning', 'info', 'debug'], default='warning',
                        help=argparse.SUPPRESS)

    args = parser.parse_args()

    event_url = args.event_url
    csv_path = args.csv_path
    buyer_path = args.buyer_path
    headless = args.headless
    process_all_by = int(args.process_all_by)
    log_level = constants.log_levels[args.log_level]

    logging.basicConfig(level=log_level)
    logger = logging.getLogger(EventTopic.PROGRESS)

    status = process_registration(event_url, csv_path, buyer_path, headless, process_all_by)
    print("Status = ", status)
