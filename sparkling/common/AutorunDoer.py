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

# embedded in python
# pip install
# same project
from sparkling.common.SomeDoer import SomeDoer

class DAutorunDoer( SomeDoer ):
    
    # Custom doer that extends functionality a bit.
    
    # for external use, my be ignored
    PREFERRED_SAVE_DIR_NAME = 'some_doer'
    
    __SAVE_FOLDER = None
    
    def __init__( self, save_folder ):
        
        super( DAutorunDoer, self ).__init__( save_folder )
            
    def autorun( self ):
        
        # Will be called externally.
        
        raise NotImplementedError

#---------------------------------------------------------------------------+++
# end 2023.10.13
# simplified
