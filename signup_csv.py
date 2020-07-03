#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 20:13:58 2020

@author: boscolau
"""

import os
import sys
import mass_signup
from buyer import Buyer
from attendee import Attendee

# Application settings
MAX = 10

if( len(sys.argv) < 3 ):
    print( "Usage: python(3) signup_csv.py <csv_file_path> <event_url> [headless]" )
    print( "\tWith 'headless', the program will run without showing the webpage in Chrome" )
    sys.exit(0)
    
    
csv_path = sys.argv[1]
event_url = sys.argv[2]

headless = False

if len(sys.argv) > 3:
    headless = True if sys.argv[3].lower() == 'headless' else False
     


if not os.path.isfile(csv_path):
    sys.exit( "CVS file does not exist.")
    
    


# Buyer is always the OLMV Mass EB organizer
buyer_FN = "OLMV"
buyer_LN = "Seattle"
buyer_email = "olmv.seattle@gmail.com"
    
buyer = Buyer().initWith( buyer_FN, buyer_LN, buyer_email )


attendee_list = list()

with open( csv_path ) as f:
    attendee_lines = f.read().splitlines()
    

# Check with MAX + 1 as the first line is headers
if len( attendee_lines) > MAX + 1:
    sys.exit( "Requests exist maximum allowed. Max = 10" )

# Remove header line=
attendee_lines.pop(0)

for line in attendee_lines :
    attendee_list.append( Attendee().initWithCSVString(line ))


"""
attendee_list.append( Attendee().initWith( last_name = "LN1", first_name = "FN1", email = "a1@b1.com", phone_number="1234567890", is_volunteer=True ) )
attendee_list.append( Attendee().initWith( last_name = "LN2", first_name = "FN2", email = "a2@b2.com", phone_number="2234567890", is_volunteer=False ) )
attendee_list.append( Attendee().initWith( last_name = "LN3", first_name = "FN3", email = "a3@b3.com", phone_number="3234567890", is_volunteer=True ) )
"""

"""
attendee_list.append( Attendee().initWithCSVString( "Bui,Dat,hahaha8111989@gmail.com,2064654809,N" ))
attendee_list.append( Attendee().initWithCSVString( "Chu,Tinh,ac@t.com,1234567890,N" ))
attendee_list.append( Attendee().initWithCSVString( "Do,Amy,quang2004@gmail.com,2068538157,N" ))
attendee_list.append( Attendee().initWithCSVString( "Do,Kim-Quy T,hanhnguyen020307@yahoo.com,206-578-3569,N" ))
attendee_list.append( Attendee().initWithCSVString( "Do,Peter,quang2004@gmail.com,206-853-8157,N" ))
attendee_list.append( Attendee().initWithCSVString( "Do,Quang,quang2004@gmail.com,206-853-8157,N" ))
attendee_list.append( Attendee().initWithCSVString( "Do,Quyen,ad@q.com,206-832-5286,N" ))
attendee_list.append( Attendee().initWithCSVString( "Duong,Maria,ad@M.com,206-468-8018,N" ))
attendee_list.append( Attendee().initWithCSVString( "Huynh,Quang,hanhnguyen020307@yahoo.com,206-405-0719,N" ))
attendee_list.append( Attendee().initWithCSVString( "Lau,Bosco,bosco.kc.lau@gmail.com,2066016801,Y" ))
"""


print( "Processing:")
print( "\tAttendee file:", csv_path)
print( "\tEvent: ", event_url )


mass_signup.signup(attendee_list, buyer, event_url, headless )

if __name__ != '__main__':
    sys.exit( "File as module not supported")
