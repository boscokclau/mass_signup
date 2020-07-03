#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 15:22:33 2020

@author: boscokclau
"""

import time
import sys
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# Application settings
WAIT_MS = 1000

# TODO: Read from CSV or other ways to identify event_id
event_id = "109437173532"

buyer_FN = "BuyerFN"
buyer_LN = "BuyerLN"
buyer_email = "bosco.kc.lau@gmail.com"

# Test data
attendee_list = list()
attendee_list.append( {"firstname": "FN_1", "lastname": "LN1", "email": "a@b.com", "phone": "1234567890", "is_volunteer": True} )
attendee_list.append( {"firstname": "FN_2", "lastname": "LN2", "email": "a2@b2.com", "phone": "2345678901", "is_volunteer": False} )
attendee_list.append( {"firstname": "FN_3", "lastname": "LN3", "email": "a3@b3.com", "phone": "3456789012", "is_volunteer": False} )

num_tickets = len(attendee_list)

driver = webdriver.Chrome( ChromeDriverManager().install())
driver.implicitly_wait( WAIT_MS )

# Go to event registration main page and click "Register" to start
# driver.get( "https://www.eventbrite.com/e/test-event-tickets-109437173532" )
# TODO: event_id is a variable only for coding purpose. Need a way to get the event URL
url = "https://www.eventbrite.com/e/test-event-tickets-" + event_id

print( "Opening: ", url )
driver.get( url )

register_button = driver.find_element_by_id( 'eventbrite-widget-modal-trigger-' + str(event_id) )

# Check if sales is open
status_text = register_button.get_attribute( 'data-tracking-label')


if status_text != 'Register':
    sys.exit("Sales has ended. No registration has been processed.")

# Space available. Continue
register_button.click()


# Select number of tickets
driver.switch_to.frame(0)


# Just sleep -- this is just a convenience script. Does not work the complexity to use explicit wait
time.sleep( WAIT_MS/1000 )

register_button = driver.find_element_by_css_selector( '.eds-btn')

# Sold out
if register_button.text != 'Register':
    print( "Sold out. No registriation has been processed" )
    
    
# Check if enough ticket for request
print( "Checking for ticket availablity for request..." )
remaining_ticket_text = driver.find_element_by_xpath( "//span[@data-spec='remaining-tickets']" )
remaining_ticket = int( remaining_ticket_text.text.split()[0] )

if remaining_ticket < len(attendee_list):
    sys.exit( f"Only {remaining_ticket} remaining. Not enough for {len(attendee_list)} attendees. No registration processed." )


print( "Tickets available. Proceeding...")
quantity_dropdown = driver.find_element_by_xpath( "//*[starts-with(@id, 'ticket-quantity-selector')]" )

# print( "button_id:", quantity_dropdown.get_attribute('id'))

quantity_select = quantity_dropdown.find_element_by_xpath( f"//option[. = '{num_tickets}']")
quantity_select.click()


register_button.click()

""" ----------------------
    Buyer informaiton
    ----------------------
"""

driver.find_element_by_id( 'buyer.N-first_name' ).click()
driver.find_element_by_id( 'buyer.N-first_name' ).send_keys( buyer_FN )

driver.find_element_by_id( 'buyer.N-last_name' ).click()
driver.find_element_by_id( 'buyer.N-last_name' ).send_keys( buyer_LN )

driver.find_element_by_id( 'buyer.N-email' ).click()
driver.find_element_by_id( 'buyer.N-email' ).send_keys( buyer_email )

driver.find_element_by_id( 'buyer.confirmEmailAddress' ).click()
driver.find_element_by_id( 'buyer.confirmEmailAddress' ).send_keys( buyer_email )

div_attendee_surveys = driver.find_elements_by_xpath( "//*[starts-with(@data-spec, 'checkout-form-survey-attendee-')]" )

num_attendees = len(div_attendee_surveys)


""" ----------------------
    Ticket informaiton
    ----------------------
"""

assert num_tickets == num_attendees, "Eventbrite might have changed the web site. Contact developer and organizer to update this application"

print( "Start entering ticket information for {0} attendees{1}...".format( num_attendees, "" if num_attendees == 1 else "s" ))

for i in range( num_attendees ):
    ticket_id = div_attendee_surveys[i].get_attribute('id')
    # print( "div id:", ticket_id )
    
    cur_attendee = attendee_list[i]
    
    print( "\tAttendee:", i + 1 )
    print( "\t\t", cur_attendee )
    
    driver.find_element_by_id( ticket_id + '.N-first_name' ).click()
    driver.find_element_by_id( ticket_id + '.N-first_name' ).send_keys( cur_attendee['firstname'] )
    
    driver.find_element_by_id( ticket_id + '.N-last_name' ).click()
    driver.find_element_by_id( ticket_id + '.N-last_name' ).send_keys( cur_attendee['lastname'] ) 
    
    driver.find_element_by_id( ticket_id + '.N-email' ).click()
    driver.find_element_by_id( ticket_id + '.N-email' ).send_keys( cur_attendee['email'] )
    

    # EB Custom Fields
    custom_fields = driver.find_elements_by_xpath( f"//*[starts-with(@name, '{ticket_id}.U-')]" )

    """
    for field in custom_fields:
        print( "ID", field.get_attribute('id') )
        print( "Name", field.get_attribute('name') )
        print()
    """
    
    
    # Phone number
    phone_textbox = custom_fields[0]
    phone_textbox.click()
    phone_textbox.send_keys( cur_attendee['phone'] )
    
    # Health screening (hs)
    hs_checkbox = custom_fields[1]
    hs_field_id = hs_checkbox.get_attribute('id')
    hs_checkbox_field = driver.find_element_by_xpath( f"//label[@for='{hs_field_id}']" )
    hs_checkbox_field.click()
    
    # Safety Instructions (si)
    si_checkbox = custom_fields[2]
    si_field_id = si_checkbox.get_attribute('id')
    si_checkbox_field = driver.find_element_by_xpath( f"//label[@for='{si_field_id}']" )
    si_checkbox_field.click()
    
    # Volunteer
    v_yes_radio = custom_fields[3]
    v_yes_field_id = v_yes_radio.get_attribute('id')
    v_yes_radio_field = driver.find_element_by_xpath( f"//label[@for='{v_yes_field_id}']" )
    
    v_no_radio = custom_fields[4]
    v_no_field_id = v_no_radio.get_attribute('id')
    v_no_radio_field = driver.find_element_by_xpath( f"//label[@for='{v_no_field_id}']" )
    
    if cur_attendee['is_volunteer']:
        v_yes_radio_field.click()
        
    if not cur_attendee['is_volunteer']:
        v_no_radio_field.click()
        
    
# EB Opt-ins/outs -- to uncheck
organizer_marketing_opt_in = driver.find_element_by_xpath( f"//label[@for='organizer-marketing-opt-in']" )
organizer_marketing_opt_in.click()

eb_marketing_opt_in = driver.find_element_by_xpath( f"//label[@for='eb-marketing-opt-in']" )
eb_marketing_opt_in.click()

# Register
register_button = driver.find_element_by_xpath( f"//button[@data-spec='eds-modal__primary-button']" )
register_button.click()

print( "\nRegistration complete. Please check email to confirm." )
