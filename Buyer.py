#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 18:04:28 2020

@author: boscolau
"""


class Buyer():
    
    # Data
    last_name = None
    first_name = None
    email = None
    
    # Think of allocating memory, like objective-C [object alloc]. Let me know
    # in the comment about this pattern to implement multiple initializers
    def __init__(self):
        pass
    
    
    # initializers
    def initWith( self, last_name, first_name, email ):
        '''
        Initialize with specific values.
        
        Parameters
        ----------
        last_name : string
        first_name : string.
        email : string.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        
        return self
        
    def __str__(self):
        return str( self.__dict__ )