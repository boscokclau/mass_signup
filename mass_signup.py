#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 15:22:33 2020

@author: boscokclau
"""

import time
from mass_signup_lib import send_progress
from constants import RegistrationStatus
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from buyer import Buyer
from attendee import Attendee

# Application settings
WAIT_MS = 1000
MAX_ALLOWED = 10


def signup(attendee_list: list, buyer: Buyer, url: str, headless: bool = False) -> (RegistrationStatus, dict):
    """
    Sign-up for seats.

    Parameters
    ----------
    attendee_list : list of Attendee
    buyer : Buyer
    url : TYPE
        Canonical EB URL.
    headless : bool
        Run browser headless if True

    Returns
    -------
    constants.RegistrationStatus
    """
    assert attendee_list
    assert buyer
    assert url

    num_tickets = len(attendee_list)

    # Quit if request is over MAX_ALLOWED
    if num_tickets > MAX_ALLOWED:
        raise ValueError(f"Request must be of less than {MAX_ALLOWED} attendees. Please break up the request to retry.")

    try:
        send_progress("Headless mode " + "on." if headless else "off.")
        if not headless:
            driver = webdriver.Chrome(ChromeDriverManager().install())

        else:
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

        driver.implicitly_wait(WAIT_MS)

        # Go to event registration main page and click "Register" to start
        event_id = url.split('-')[-1]

        send_progress("Opening: " + url)
        driver.get(url)

        register_button = driver.find_element_by_id('eventbrite-widget-modal-trigger-' + str(event_id))

        # Check if sales is open
        status_text = register_button.get_attribute('data-tracking-label')

        if status_text != 'Register':
            send_progress("Sales has ended. No registration has been processed.")
            return RegistrationStatus.SALES_ENDED, dict()

        # Space available. Continue
        register_button.click()

        # Select number of tickets
        driver.switch_to.frame(0)

        # Just sleep -- this is just a convenience script. Does not work the complexity to use explicit wait
        time.sleep(WAIT_MS / 1000)

        register_button = driver.find_element_by_css_selector('.eds-btn')
        print("reg button", register_button)
        time.sleep(WAIT_MS / 500)
        # Sold out, Button is Detail to waiting list registration
        #if register_button.text != 'Register':
        #    send_progress("Line 91. Registration Button not detected. Sold out. No registration has been processed")
        #    return RegistrationStatus.SOLD_OUT, dict()

        # Check if enough ticket for request
        send_progress("Checking for ticket availability for request...")
        time.sleep(WAIT_MS / 333)
        remaining_ticket_text = driver.find_element_by_xpath("//span[@data-spec='remaining-tickets']")
        remaining_ticket = int(remaining_ticket_text.text.split()[0])

        if remaining_ticket < len(attendee_list):
            send_progress(
                f"Only {remaining_ticket} remaining. Not enough for {len(attendee_list)} attendees. No registration processed.")
            return RegistrationStatus.NOT_ENOUGH_SEATS, {"remaining": remaining_ticket}

        send_progress("Tickets available. Proceeding...")
        quantity_dropdown = driver.find_element_by_xpath("//*[starts-with(@id, 'ticket-quantity-selector')]")

        quantity_select = quantity_dropdown.find_element_by_xpath(f"//option[. = '{num_tickets}']")
        quantity_select.click()

        register_button.click()

        """ ----------------------
            Buyer information
            ----------------------
        """

        driver.find_element_by_id('buyer.N-first_name').click()
        driver.find_element_by_id('buyer.N-first_name').send_keys(buyer.first_name)

        driver.find_element_by_id('buyer.N-last_name').click()
        driver.find_element_by_id('buyer.N-last_name').send_keys(buyer.last_name)

        driver.find_element_by_id('buyer.N-email').click()
        driver.find_element_by_id('buyer.N-email').send_keys(buyer.email)

        driver.find_element_by_id('buyer.confirmEmailAddress').click()
        driver.find_element_by_id('buyer.confirmEmailAddress').send_keys(buyer.email)

        div_attendee_surveys = driver.find_elements_by_xpath(
            "//*[starts-with(@data-spec, 'checkout-form-survey-attendee-')]")

        num_attendees = len(div_attendee_surveys)

        """ ----------------------
            Ticket information
            ----------------------
        """

        assert num_tickets == num_attendees, "Eventbrite might have changed the web site. Contact developer and organizer to update this application"

        send_progress("Start entering ticket information for {0} attendees{1}...".format(num_attendees,
                                                                                         "" if num_attendees == 1 else "s"))

        for i, cur_attendee in enumerate(attendee_list):
            ticket_id = div_attendee_surveys[i].get_attribute('id')

            send_progress(f"\tAttendee: {i + 1:2d} -- \n\t{cur_attendee}")

            driver.find_element_by_id(ticket_id + '.N-first_name').click()
            driver.find_element_by_id(ticket_id + '.N-first_name').send_keys(cur_attendee.first_name)

            driver.find_element_by_id(ticket_id + '.N-last_name').click()
            driver.find_element_by_id(ticket_id + '.N-last_name').send_keys(cur_attendee.last_name)

            driver.find_element_by_id(ticket_id + '.N-email').click()
            driver.find_element_by_id(ticket_id + '.N-email').send_keys(
                cur_attendee.email if cur_attendee.email is not None and len(cur_attendee.email) != 0 else buyer.email)

            # EB Custom Fields
            custom_fields = driver.find_elements_by_xpath(f"//*[starts-with(@name, '{ticket_id}.U-')]")

            # Phone number
            phone_textbox = custom_fields[0]
            phone_textbox.click()
            phone_textbox.send_keys(cur_attendee.phone_number if cur_attendee.phone_number is not None and len(
                cur_attendee.phone_number) != 0 else 'NA')

            # Health screening (hs)
            hs_checkbox = custom_fields[1]
            hs_field_id = hs_checkbox.get_attribute('id')
            hs_checkbox_field = driver.find_element_by_xpath(f"//label[@for='{hs_field_id}']")
            hs_checkbox_field.click()

            # Safety Instructions (si)
            si_checkbox = custom_fields[2]
            si_field_id = si_checkbox.get_attribute('id')
            si_checkbox_field = driver.find_element_by_xpath(f"//label[@for='{si_field_id}']")
            si_checkbox_field.click()

            # Volunteer
            v_yes_radio = custom_fields[3]
            v_yes_field_id = v_yes_radio.get_attribute('id')
            v_yes_radio_field = driver.find_element_by_xpath(f"//label[@for='{v_yes_field_id}']")

            v_no_radio = custom_fields[4]
            v_no_field_id = v_no_radio.get_attribute('id')
            v_no_radio_field = driver.find_element_by_xpath(f"//label[@for='{v_no_field_id}']")

            if cur_attendee.is_volunteer:
                v_yes_radio_field.click()
            else:
                v_no_radio_field.click()

        # EB Opt-ins/outs -- to uncheck
        organizer_marketing_opt_in = driver.find_element_by_xpath(f"//label[@for='organizer-marketing-opt-in']")
        organizer_marketing_opt_in.click()

        eb_marketing_opt_in = driver.find_element_by_xpath(f"//label[@for='eb-marketing-opt-in']")
        eb_marketing_opt_in.click()

        # Register
        register_button = driver.find_element_by_xpath(f"//button[@data-spec='eds-modal__primary-button']")
        register_button.click()

        send_progress("Waiting for web response")

        for i in range(10):
            send_progress(str(10 - i) + " second{} remaining".format('s' if 10 - i > 1 else ''))
            time.sleep(1)

        order_id = driver.find_element_by_xpath(f"//h4[@data-spec='confirmation-order-id']").text
        send_progress(f"\nRegistration complete. Order ID: {order_id}. \nPlease check email to confirm.")
    except BaseException as e:
        send_progress(
            f"Unexpected error has occurred. Check email or contact organizer to confirm registration.\n {repr(e)}")
        return RegistrationStatus.UNEXPECTED_ERROR, {"error": repr(e)}
    finally:
        driver.quit()

    return RegistrationStatus.COMPLETED, {"order_id": order_id}
