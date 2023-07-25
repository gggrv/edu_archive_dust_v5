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

class SomeDoer:
    
    # Whenever I want to use application's `data` folder,
    # i create a custom version of this class.
    # This custom version has access to specific
    # data/save_folder and manages it however it wants
    # whitout bothering anything outside.
    
    __SAVE_FOLDER = None
    
    # for external use, my be ignored
    PREFERRED_SAVE_DIR_NAME = 'some_doer'
    
    def __init__( self,
        save_folder
        ):
        
        # these cannot be changed
        self.__set_save_folder( save_folder )
        
    def get_save_folder( self ):
        
        return self.__SAVE_FOLDER
        
    def __set_save_folder( self, path ):
            
        # make sure it exists
        if not os.path.isdir( path ):
            os.makedirs( path )
            
        self.__SAVE_FOLDER = path
        
    def set_file( self, filename ):
        
        src = os.path.join(
            self.__SAVE_FOLDER, filename )
        
        return src
        
    def set_folder( self, dirname ):
        
        src = os.path.join(
            self.__SAVE_FOLDER, dirname )
        
        # make sure it exists
        if not os.path.isdir( src ):
            os.makedirs( src )
            
        return src
            
    def autorun( self ):
        
        # Will be called externally.
        
        pass #raise NotImplementedError

#---------------------------------------------------------------------------+++
# end 2023.07.14
# removed `generate_files` because useless
