# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import os
# same project
from sparkling.common import savef_yaml, readf_yaml
    
class PresetManager:
    
    _presets = None # future dictionary
    
    __file_name = None # future path
    
    def __init__( self, file_name ):
        
        self.__file_name = file_name
        
    def get_presets( self ):
        
        # Returns saved presets.
        
        they_exist = os.path.isfile( self.__file_name )
        has_in_memory = not ( self._presets is None )
        
        if has_in_memory:
            return self._presets
        elif they_exist:
            self._presets = readf_yaml( self.__file_name )
            return self._presets
        
        log.error( 'no presets exist yet, not doing anything' )
        return {}
        
    def new_preset(
            self,
            unique_name, *args ):
        
        raise NotImplementedError
        
        self._save_all_presets()
        
    def delete_preset( self, unique_name ):
        
        # Deletes only one preset.
        
        if not unique_name in self._presets:
            log.error( 'no such preset, not doing anything' )
            return
        
        self._presets.pop( unique_name )
        
        self._save_all_presets()
        
    def clear_all_presets( self ):
        
        self._presets = None
        
        # Completely resets corresponding subfolder.
        
        if not os.path.exists( self.__file_name ):
            # it does not exist, nothing to clear
            log.warning( 'attempted to clear non-existant file' )
            return
            
        os.remove( self.__file_name )
        
        log.debug( 'successfully cleared file' )
        
    def _save_all_presets( self ):
        
        savef_yaml( self.__file_name, self._presets )

#---------------------------------------------------------------------------+++
# end 2023.03.18
# created