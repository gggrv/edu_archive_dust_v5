# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
from sparkling.common.SomeDoer import SomeDoer
        
class MainDoer( SomeDoer ):
    
    # `Main doer` of the host application.
    # Currently empty, may
    # do something useful in the future.
    
    PREFERRED_SAVE_DIR_NAME = 'host_qtapp'
    
    # Doer hierarchy:
    # ■ `data` folder = `sparkling.SomeDoer`
    # └─■ `data/PREFERRED_SAVE_DIR_NAME` = this doer
    #   └─■ `data/PREFERRED_SAVE_DIR_NAME/some_other_folder` = some other doer
        
    def __init__( self, save_folder ):
        
        super( MainDoer, self ).__init__( save_folder )
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
