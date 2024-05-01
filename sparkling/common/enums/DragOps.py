# -*- coding: utf-8 -*-
#BSD Zero Clause License
#
#Copyright (C) 2023 by Anna Anikina
#
#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted.
#
#THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
