# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

class EDragOps:
    
    @staticmethod
    def encode_flags(
        accept_external_drops, # drop new items from anywhere
        accept_internal_drops, # internal move (reposition rows)
        ):
        
        # This function creates a binary number
        # that describes allowed functionality.
        
        # this array will contain last -> first digit
        # of a custom binary number
        reversed_binary_values = [
            '1' if accept_external_drops else '0',
            '1' if accept_internal_drops else '0',
            ]
            
        binary_string = ''.join( reversed_binary_values[::-1] )
        
        return int( binary_string, 2 )
                
    @staticmethod
    def decode_flags( value ):
        
        pass
        
#---------------------------------------------------------------------------+++
# end 2023.10.12
# created
