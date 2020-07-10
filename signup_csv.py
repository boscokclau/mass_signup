#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import os
import sys
import argparse
import mass_signup
from constants import ProgramStatus
from buyer import Buyer
from attendee import Attendee

# Application settings
MAX = 10


def process_registration(event_url: str, csv_path: str, headless: bool = False):
    # Buyer is always the OLMV Mass EB organizer
    buyer_FN = "OLMV"
    buyer_LN = "Seattle"
    buyer_email = "olmv.seattle@gmail.com"

    buyer = Buyer(buyer_FN, buyer_LN, buyer_email)

    attendee_list = list()

    with open(csv_path) as f:
        attendee_lines = f.read().splitlines()

    # Check with MAX + 1 as the first line is headers
    if len(attendee_lines) > MAX + 1:
        print(f"Requests exist maximum allowed. Max = {MAX}")
        return ProgramStatus.CONSTRAINT_VIOLATION

    # Remove header line=
    attendee_lines.pop(0)

    for line in attendee_lines:
        attendee = Attendee.from_csv_string(line)
        attendee_list.append(attendee)

    print("Processing:")
    print("\tAttendee file:", csv_path)
    print("\tEvent: ", event_url)
    print()

    return mass_signup.signup(attendee_list, buyer, event_url, headless)


# Program Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('event_url', help='URL of the EventBrite event.')
    parser.add_argument('csv_path', help='File path to the attendee CSV file.')
    parser.add_argument('-c', '--command-line-mode', dest='headless', help='Command line mode. Run browser headless.',
                        action='store_true')
    args = parser.parse_args()

    event_url = args.event_url
    csv_path = args.csv_path
    headless = args.headless

    process_registration(event_url, csv_path, headless)
