# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Tools for ConTeXt projects.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.common.SomeDoer import SomeDoer
from sparkling.contech.Conventions import Conventions
from sparkling.contech.main import (
    render_product, get_products
    )
from sparkling.common import savef

class ContextProject( SomeDoer ):
    
    # A definition of some existing context project.
    # Gives easy access to necessary files.
    # Assumes the project follows naming conventions.
    
    __project_name = None
    
    __products = None
    
    class Files:
        
        ENVIRONMENT_DEFINITION = None
        PROJECT_DEFINITION = None
    
    def __init__(
            self,
            project_root_folder
            ):
        
        # make sure given project_root_folder has appropriate prefix
        basename = os.path.basename( project_root_folder )
        if not Conventions.PROJECT_NAME_PREFIX in basename:
            raise NameError( f'please include {Conventions.PROJECT_NAME_PREFIX} in the project directory name' )
            
        # proceed to set up doer's folder
        super( ContextProject, self ).__init__( project_root_folder )
        
        # remember unprefixed project name
        self.__project_name = basename.replace( Conventions.PROJECT_NAME_PREFIX, '' )
        
        # set paths
        self.Files.ENVIRONMENT = self.set_file(
            f'{Conventions.ENVIRONMENT_NAME_PREFIX}{self.__project_name}.tex' )
        self.Files.PROJECT_DEFINITION = self.set_file(
            f'{Conventions.PROJECT_NAME_PREFIX}{self.__project_name}.tex' )
        
        # dynamic
        self.__products = {}
        
        # make sure needed files exist
        self.default_environment_definition()
        self.default_project_definition()
    
    def project_name( self ):
        return self.__project_name
        
    def default_environment_definition( self ):
        
        src = self.Files.ENVIRONMENT
        
        if os.path.isfile( src ):
            log.info( f'file already exists: {src}, not doing anything' )
            return
        
        text = Conventions.default_environment_definition( self.__project_name )
        
        savef( src, text )
        
    def default_project_definition( self ):
        
        src = self.Files.PROJECT_DEFINITION
        
        if os.path.isfile( src ):
            log.info( f'file already exists: {src}, not doing anything' )
            return
        
        text = Conventions.default_project_definition( self.__project_name )
        
        savef( src, text )
    
    def get_products( self, force_refresh=False ):
        
        if len( self.__products )==0 or force_refresh:
            self.__products = get_products( self.__project_root_folder )
            
        return self.__products
    
    def render_product( self, product, custom_context_console_command=None ):
        
        # get src
        
        src = None
        if product in self.__products:
            # i gave product name
            src = self.__products[product]
        elif product is self.__products.values():
            # i gave product path
            src = product
        elif os.path.isfile(product):
            # i gave product path
            src = product
            log.warning( f'the product you want to render is not part of this project: {src}' )
        else:
            # i gave something unknown
            raise ValueError( f'unknown product: {src}' )
        
        # render it
        
        if custom_context_console_command is None:
            render_product( src )
        else:
            render_product(
                src,
                context_console_command=custom_context_console_command
                )
    
#---------------------------------------------------------------------------+++
# end 2023.05.22
# fixed method names
