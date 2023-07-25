# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
from sparkling.common.PresetManager import PresetManager
    
class Columns:
    
    LABELS = 'labels'
    SCREEN_NAME = 'screen_name'
    DB_NAME = 'db_name'
    RULE = 'rule'
    DESCRIPTION = 'desc'
    
class FileRenamerPresets( PresetManager ):
    
    Columns = Columns
    
    def __init__( self, file_name ):
        
        super( FileRenamerPresets, self ).__init__( file_name )

#---------------------------------------------------------------------------+++
# end 2023.07.25
# simplified
