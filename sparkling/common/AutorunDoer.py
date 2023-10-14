# -*- coding: utf-8 -*-

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
