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
import os
# pip install
# same project
from sparkling.common import savef_yaml, readf_yaml
    
class PresetManager:
    
    _presets = None # future dictionary
    __SAVE_FILE = None # future path
    
    def __init__( self, save_file ):
        
        self.__SAVE_FILE = save_file
        self._presets = {}
        
    def presets( self, rescan=False ):
        
        # Gets all existing presets.
        
        they_exist = os.path.isfile( self.__SAVE_FILE )
        has_in_memory = len(self._presets) > 0
        
        if has_in_memory and not rescan:
            return self._presets
        elif they_exist:
            self._presets = readf_yaml( self.__SAVE_FILE )
            return self._presets
        
        log.error( 'no presets exist yet' )
        return self._presets
    
    def preset( self, unique_name, rescan=False ):
        
        # Gets specific preset from existing ones.
        
        try:
            ps = self.presets( rescan=rescan )
            return ps[ unique_name ]
        except KeyError:
            # this preset does not exist yet
            pass
            
    def save_preset(
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
        
    def _save_all_presets( self ):
        
        savef_yaml( self.__SAVE_FILE, self._presets )
        
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
        
        # Completely resets corresponding file.
            
        self._presets = None
        
        if not os.path.exists( self.__SAVE_FILE ):
            # it does not exist, nothing to clear
            #log.info( 'attempted to clear non-existant file' )
            return
            
        os.remove( self.__SAVE_FILE )
        #log.debug( 'successfully cleared file' )

#---------------------------------------------------------------------------+++
# end 2023.10.19
# fix force_reread