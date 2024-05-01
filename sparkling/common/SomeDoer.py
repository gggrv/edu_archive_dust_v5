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

class SomeDoer:
    
    # This class can manage given `save folder`
    # however it wants
    # without bothering anything outside.
    
    __SAVE_FOLDER = None
    
    # for external use only, may be ignored
    PREFERRED_SAVE_DIR_NAME = 'some_doer'
    
    def __init__( self, save_folder ):
        # set it once and never change
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

#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
