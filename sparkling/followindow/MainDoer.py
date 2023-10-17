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
from sparkling.common import ( savef, readf_yaml )
from sparkling.common.AutorunDoer import DAutorunDoer

def generate_custom_gestures( src ):
        
    text = """---
# please define custom gestures here
# gestures are invoked by holding right mouse button inside the followindow
# U=up, D=down, L=left, R=right
# some method that will be eval(..): [moosegesture]
self.tray_menu_toggle(): ['DR','U','DL'] # draw a cross to close this followindow
self._request_custom_program_event('grimoire'): ['D'] # swipe down to summon grimoire
..."""
        
    savef( src, text )
        
class MainDoer( DAutorunDoer ):
    
    PREFERRED_SAVE_DIR_NAME = 'followindow'
    
    class Files:
        ICON = 'grimoire.png'
        CUSTOM_GESTURES = 'custom_gestures.yaml'
    
    __gestures = None
    
    def __init__( self, save_folder ):
        
        super( MainDoer, self ).__init__( save_folder )

        # set files
        self.Files.CUSTOM_GESTURES = self.set_file( self.Files.CUSTOM_GESTURES )
        self.Files.ICON = self.set_file( self.Files.ICON )
        
        # dynamic
        self.__gestures = {}
        
    def _load_gestures( self ):
        
        # Reads gesture definitions from disk.
        
        # TODO
        # do it safely
        
        src = self.Files.CUSTOM_GESTURES
        if not os.path.isfile( src ):
            log.error( f'no custom gestures found, generating default ones: {src}' )
            # make deafault ones
            generate_custom_gestures( src )
            # prompt user to edit them
            os.startfile( src )
        
        # read file from disk
        self.__gestures = readf_yaml(src)
        
    def get_gestures( self ):
        
        # For external use only.
        
        if len( self.__gestures )==0:
            self._load_gestures()
        
        return self.__gestures
    
    def autorun( self ):
        return True, 'ok'
        
#---------------------------------------------------------------------------+++
# end 2023.10.17
# switched correct doer
