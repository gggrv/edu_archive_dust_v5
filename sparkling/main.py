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
from sparkling.SomeDoer import SomeDoer
    
class MainPaths:
    
    # This is a static class that should provide
    # reliable info about project folder structure.
    # Single source of truth.
    
    # Expected folder structure:
    # ■ `Project` or `application`
    # ├─■ folder with all the python code, `code root`
    # │ ├─■ this file
    # │ └─■ anything else
    # ├─■ `data` folder with user data or programmatically saved data
    # └─■ application entry point that calls code from the `code root`
    
    # set them once and never change
    __CODE_ROOT = os.path.dirname( __file__ )
    __APPLICATION_ROOT = os.path.dirname( __CODE_ROOT )
    __DATA_ROOT = os.path.join( __APPLICATION_ROOT, 'data' )
    
    # i may need `some doer` in order to manage the `data` folder
    # in a standardised fashion
    # currently the most simple one is ok,
    # but in the future i may want to subclass it
    # and define some app-wide operatons
    __MainDoer = None
    
    @staticmethod
    def code_root():
        # Returns the root folder of the main code.
        return MainPaths.__CODE_ROOT
    
    @staticmethod
    def application_root():
        # Returns the root folder of this application.
        return MainPaths.__APPLICATION_ROOT
    
    @staticmethod
    def data_root():
        # Returns the root folder of the user
        # customizeable data folder
        # that is managed by __MasterDoer.
        return MainPaths.__DATA_ROOT
    
    @staticmethod
    def __main_doer():
        
        # This is a core doer that manages `data` folder.
        # For internal use only.
        
        # make sure it exists
        if( MainPaths.__MainDoer is None ):
            MainPaths.__MainDoer = SomeDoer( MainPaths.__DATA_ROOT )
            
        return MainPaths.__MainDoer
        
    @staticmethod
    def set_file( filename ):
        OwnDoer = MainPaths.__main_doer()
        src = OwnDoer.set_file( filename )
        return src
        
    @staticmethod
    def set_folder( dirname ):
        OwnDoer = MainPaths.__main_doer()
        src = OwnDoer.set_folder( dirname )
        return src

#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
