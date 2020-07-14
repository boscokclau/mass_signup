#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import argparse
import mass_signup
from buyer import Buyer
from attendee import Attendee


# Application setting

def process_registration(event_url: str, csv_path: str, headless: bool = False, process_all_by: int = 0):
    # Buyer is always the OLMV Mass EB organizer
    buyer_FN = "OLMV"
    buyer_LN = "Seattle"
    buyer_email = "olmv.seattle@gmail.com"

    buyer = Buyer(buyer_FN, buyer_LN, buyer_email)

    attendee_list = list()

    with open(csv_path) as f:
        attendee_lines = f.read().splitlines()

    # Remove header line=
    attendee_lines.pop(0)

    for line in attendee_lines:
        attendee = Attendee.from_csv_string(line)
        attendee_list.append(attendee)

    attendee_list_collections = list()
    if process_all_by != 0:
        attendee_list_collections = [attendee_list[i:i + process_all_by] for i in
                                     range(0, len(attendee_list), process_all_by)]
    else:
        attendee_list_collections.append(attendee_list)

    print("Processing:")
    print("\tAttendee file:", csv_path)
    print("\tEvent: ", event_url)
    print()

    status_all = 0
    for i, a_list in enumerate(attendee_list_collections):
        print("Order:", i + 1)
        status = mass_signup.signup(a_list, buyer, event_url, headless)

        print("status: ", status)

        # status != 0 means something might have gone wrong. Set bit to indicate which order had a problem
        if status:
            status_all = status_all | 1 << i

    return status_all


# Program Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('event_url', help='URL of the EventBrite event.')
    parser.add_argument('csv_path', help='File path to the attendee CSV file.')
    parser.add_argument('-c', '--command-line-mode', dest='headless', help='Command line mode. Run browser headless.',
                        action='store_true')
    parser.add_argument('-a', '-all_by', dest='process_all_by', default=0, help=argparse.SUPPRESS)

    args = parser.parse_args()

    event_url = args.event_url
    csv_path = args.csv_path
    headless = args.headless
    process_all_by = int(args.process_all_by)

    status = process_registration(event_url, csv_path, headless, process_all_by)
    print("Status = ", status)
