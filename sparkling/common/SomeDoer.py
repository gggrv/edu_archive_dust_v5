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
    
    # future dictionary
    _generate_file_functions = None
    
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
    
    def generate_files( self, src_list, force_list ):
        
        # Standard interface for generating automatic files.
        # Either only missing are generated,
        # or all are overwritten by default ones.
        
        if self._generate_file_functions is None:
            raise NotImplementedError
            
        expected_len = len( self._generate_file_functions )
        
        # propagate force
        if type(force_list) == bool:
            force_list = [ force_list for _ in range(expected_len) ]
            
        # foolcheck
        received_len = len(src_list)
        if not( received_len==len(force_list)
            and expected_len==received_len
            ):    
            raise IndexError
            
        # call dedicated functions
        for iloc in range( expected_len ):
            
            # get settings
            src = src_list[iloc]
            k = os.path.basename(src)
            force = force_list[iloc]
            func = self._generate_file_functions[k]
            
            # call appropriate function
            if os.path.exists( src ) and not force:
                log.info( f'skipping generation - file already exists: {src}' )
            else:
                func( src )
                log.debug( f'successfully wrote file: {src}' )
            
    def autorun( self ):
        
        # Will be called externally.
        
        pass #raise NotImplementedError

#---------------------------------------------------------------------------+++
# end 2023.05.11
# updated
