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
        self._presets = {}
        
    def presets( self, force_reread=False ):
        
        # Gets all existing presets.
        
        they_exist = os.path.isfile( self.__file_name )
        has_in_memory = len(self._presets) > 0
        
        if has_in_memory and not force_reread:
            return self._presets
        elif they_exist:
            self._presets = readf_yaml( self.__file_name )
            return self._presets
        
        log.error( 'no presets exist yet' )
        return self._presets
    
    def preset( self, unique_name, force_reread=False ):
        
        # Gets specific preset from existing ones.
        
        try:
            ps = self.presets( force_reread=force_reread )
            return ps[ unique_name ]
        except KeyError:
            # this preset does not exist yet
            pass
            
    def new_preset(
            self,
            unique_name, row_dictionary
            ):
            
        if self._presets is None:
            # im creating first preset ever
            
            self._presets = {
                unique_name: row_dictionary
                }
            
        else:
            # im adding new to some already existing
            self._presets[unique_name] = row_dictionary
            
        self._save_all_presets()
        
    def delete_preset( self, unique_name ):
        
        # Deletes only one preset.
        
        try:
            # load them
            self.presets()
            self._presets.pop( unique_name )
            self._save_all_presets()
        except KeyError:
            log.error( 'no such preset, not doing anything' )
        
    def clear_all_presets( self ):
        
        # Completely resets corresponding subfolder.
            
        self._presets = None
        
        if not os.path.exists( self.__file_name ):
            # it does not exist, nothing to clear
            #log.info( 'attempted to clear non-existant file' )
            return
            
        os.remove( self.__file_name )
        #log.debug( 'successfully cleared file' )
        
    def _save_all_presets( self ):
        
        savef_yaml( self.__file_name, self._presets )

#---------------------------------------------------------------------------+++
# end 2023.07.25
# allowed subclasses to access `_presets`