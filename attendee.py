#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 18:49:57 2020

@author: boscolau
"""


class Attendee:
    
    # Data
    last_name = None
    first_name = None
    email = None
    phone_number = None
    is_volunteer = None
    
    # Think of allocating memory, like objective-C [object alloc]. Let me know
    # in the comment about this pattern to implement multiple initializers
    def __init__(self):
        pass
    
    # initializers
    def initWith(self, last_name, first_name, email, phone_number=None, is_volunteer=False):
        '''
        Initilize with specific values

        Parameters
        ----------
        last_name : string
        first_name : string
        email : string
        phone_number : string, optional
            The default is None.
        is_volunteer : boolean, optional
            The default is False.

        Returns
        -------
        self.

        '''
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone_number = phone_number
        self.is_volunteer = is_volunteer
        
        return self
    
    
    def initWithCSVString( self, csvString ):
        '''
        Create an Attendee object given the csvString. The csvString has the following fields:
            last_name, first_name, email, phone_number, isVolunteer (of value "Y" or "N")

        Parameters
        ----------
        csvString : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        fields = csvString.split(',')
        last_name = fields[0]
        first_name = fields[1]
        email = fields[2]
        phone_number = fields[3]
        is_volunteer = True if fields[4].upper() == "Y" else False
        
        return self.initWith( last_name, first_name, email, phone_number, is_volunteer )
    
    
        
    def __str__(self):
        return str( self.__dict__ )