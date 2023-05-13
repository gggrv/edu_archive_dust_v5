# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.common import (
    savef, readf_yaml )
from sparkling.common.SomeDoer import (
    SomeDoer as BaseSomeDoer )

def generate_custom_gestures( src ):
        
    text = """---
# eval( python_method(some_params) ): [moosegesture]
self.tray_menu_toggle(): ['DR','U','DL']
self._request_custom_program_event('grimoire'): ['D']
..."""
        
    savef( src, text )
        
class MainDoer( BaseSomeDoer ):
    
    PREFERRED_SAVE_DIR_NAME = 'followindow'
    
    class Files:
        ICON = 'grimoire.png'
        CUSTOM_GESTURES = 'custom_gestures.yaml'
        
    _generate_file_functions = {
        Files.CUSTOM_GESTURES: generate_custom_gestures,
        }
    
    __gestures = None
    
    def __init__( self, save_folder ):
        
        super( MainDoer, self ).__init__( save_folder )

        # set files
        self.Files.CUSTOM_GESTURES = self.set_file( self.Files.CUSTOM_GESTURES )
        self.Files.ICON = self.set_file( self.Files.ICON )
        
    def get_gestures( self, force=False ):
        
        need_to_read = self.__gestures is None or force
        if not need_to_read:
            return self.__gestures
        
        src = self.Files.CUSTOM_GESTURES
        if not os.path.isfile( src ):
            log.error( f'no custom gestures found: {src}' )
            self.__gestures = {}
            return
        
        # TODO
        # do it safely
        
        self.__gestures = readf_yaml(src)
        log.debug( f'successfully reloaded gestures from {src}' )
        
        return self.__gestures
        
#---------------------------------------------------------------------------+++
# end 2023.05.11
# separated from another file
