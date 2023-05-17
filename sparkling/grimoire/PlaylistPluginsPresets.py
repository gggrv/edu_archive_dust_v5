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
        
    def new_preset(
            self,
            unique_name,
            enabled_plugins
            ):
        
        # Saves preset.
        
        c = Columns
        
        # add new
        
        row = {
            c.ENABLED_PLUGINS: enabled_plugins
            }
            
        if self._presets is None:
            # im creating first preset ever
            
            self._presets = {
                unique_name: row
                }
            
        else:
            # im adding new / replacing same existing
            self._presets[unique_name] = row
            
        self._save_all_presets()

#---------------------------------------------------------------------------+++
# end 2023.05.17
# created
