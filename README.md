# mass_signup

## What it is
A python application screen scraping an EventBrite ordering page to do repeating sign-ups to attend Sunday Mass at Our Lady of Mount Virgin Church in Seattle, USA.

## Who use the application
Mass coordinators who keep a list of repeating worshipers who are not tech-savy to signup online. Insted of manually entering 20+ tikcets very week, this application reads a CSV file (see below) and do registrations with one command.

## Technical details
This application uses the python selenium library to parse the web page. For the purpose of building the application, Chrome is hardcoded as the webdriver. Driver version is auto-detected by WebDriverManager. The application should download drivers of Chrome versions on the computer if necessary.
