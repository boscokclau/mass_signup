# mass_signup

## What it is
A python application screen scraping an EventBrite ordering page to do repeating sign-ups to attend Sunday Mass at Our Lady of Mount Virgin Church in Seattle, USA. The repository consists code for two versions:
- Command line, by executing signup_csv.py
- Windowing application, by executing mass_signup_ui.py

Both applications has `#!/usr/bin/env python3` at the top to make itself executable

At this moment, the application is written only for OLMV, hence the default buyer of tickets.

The application assumes the screen has the following fields:

- Buyer
    - First Name
    - Last Name
    - Email
- Each registrant
    - First Name
    - Last Name
    - Email
    - Phone Number -- A custom form because of the need to define multi-lingual field name
    - Two custom checkbox fields, for agreements
    - One option set of two options, to indicate volunteering
    - Two Eventbrite checkboxes for marketing material, which the script will uncheck
    
The CSV file are to have the following fields for each registrant, in order"
1. Last Name
2. First Name
3. Email
4. Phone Number
5. Is Volunteer, with value of either "Y", "N", or empty, with empty means "N"




## Who use the application
Mass coordinators who keep a list of repeating worshipers who are not tech-savy to signup online. Insted of manually entering 20+ tikcets very week, this application reads a CSV file (see above) and do registrations with one command.

## Technical details
This application uses the python selenium library to parse the web page. For the purpose of building the application, Chrome is hardcoded as the webdriver. Driver version is auto-detected by WebDriverManager. The application should download drivers of Chrome versions on the computer if necessary.
