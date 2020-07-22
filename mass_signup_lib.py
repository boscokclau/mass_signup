# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import logging
from pubsub import pub

from constants import EventTopic
from attendee import Attendee


def get_attendees_from_csv(csv_path: str, process_all_by: int = 0) -> list:
    """
    Parameters
    ----------
    csv_path
        Path to CSV file, of which data of attendees are recorded
    process_all_by
        Number of attendees in a group of attendees for one order. 0 means all attendees in one order

    Returns
    -------
        List of list of attendees in one order
    """
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

    return attendee_list_collections


def send_progress(msg:str):
    logger = logging.getLogger(EventTopic.PROGRESS)
    logger.info(msg)
    pub.sendMessage(EventTopic.PROGRESS, msg=msg)
