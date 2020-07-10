#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 18:49:57 2020

@author: boscolau
"""


class Attendee:

    # Default constructor
    def __init__(self, last_name: str, first_name: str, email: str, phone_number: str = None,
                 is_volunteer: bool = False):
        """
        Default constructor

        Parameters
        ----------
        last_name : str
        first_name : str
        email : str
        phone_number : str, optional
            The default is None.
        is_volunteer : boolean, optional
            The default is False.
        """
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone_number = phone_number
        self.is_volunteer = is_volunteer

    # Constructor methods
    @classmethod
    def from_csv_string(cls, csv_string: str):
        """
        Create an Attendee object given the csv_string. The csv_string has the following fields:
            last_name, first_name, email, phone_number, isVolunteer (of value "Y" or "N")

        Parameters
        ----------
        csv_string : str
            CSV string representing data of an attendee

        Returns
        -------
        Attendee
            An Attendee object created with data from csv_string.
        """
        last_name, first_name, email, phone_number, is_volunteer = csv_string.split(',')
        is_volunteer = True if is_volunteer.upper() == "Y" else False
        return cls(last_name, first_name, email, phone_number, is_volunteer)

    def __str__(self):
        return str(self.__dict__)
