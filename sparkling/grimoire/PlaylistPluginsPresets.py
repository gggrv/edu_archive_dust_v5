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
    
    ENABLED_PLUGINS = 'load'
    
class PlaylistPluginsPresets( PresetManager ):
    
    # Creates different preset settings for physical fonts.
    # These settings define logical fonts derived from physical ones.
    
    Columns = Columns
    
    def __init__( self, file_name ):
        
        super( PlaylistPluginsPresets, self ).__init__( file_name )

#---------------------------------------------------------------------------+++
# end 2023.05.25
# simplified
