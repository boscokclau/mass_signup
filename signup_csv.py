#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import sys
import mass_signup
from buyer import Buyer
from attendee import Attendee


if( len(sys.argv) != 3 ):
    print( "Usage: python(3) signup_csv.py <csv_file_path> <event_url>" )
    sys.exit(0)
    
    
csv_path = sys.argv[1]
event_url = sys.argv[2]

# Buyer is always the OLMV Mass EB organizer
buyer_FN = "OLMV"
buyer_LN = "Seattle"
buyer_email = "olmv.seattle@gmail.com"
    
buyer = Buyer().initWith( buyer_FN, buyer_LN, buyer_email )


attendee_list = list()
attendee_list.append( Attendee().initWith( last_name = "LN1", first_name = "FN1", email = "a1@b1.com", phone_number="1234567890", is_volunteer=True ) )
attendee_list.append( Attendee().initWith( last_name = "LN2", first_name = "FN2", email = "a2@b2.com", phone_number="2234567890", is_volunteer=False ) )
attendee_list.append( Attendee().initWith( last_name = "LN3", first_name = "FN3", email = "a3@b3.com", phone_number="3234567890", is_volunteer=True ) )

print( "Processing:")
print( "\tAttendee file:", csv_path)
print( "\tEvent: ", event_url )


mass_signup.signup(attendee_list, buyer, event_url)

if __name__ != '__main__':
    sys.exit( "File as module not supported")
