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
from sparkling.contech.Conventions import Conventions as Conv
from sparkling.contech.tools import (
    render_product, get_products
    )
from sparkling.common import savef

class ContextProject( object ):
    
    # A definition of the project.
    # Gives easy eccess to necessary files.
    # Assumes the project follows naming conventions.
    
    __project_root_folder = None
    __project_name = None
    
    __products = None
    
    class Files:
        
        ENVIRONMENT = None #'env_{}.tex'
        PROJECT_DEFINITION = None #'project_{}.tex'
    
    def __init__(
            self,
            project_root_folder,
            project_name=None
            ):
        
        super( ContextProject, self ).__init__()
        
        self.__set_root_folder( project_root_folder )
        self.__set_project_name( project_name )
        
        self.__products = {}
        
        # set files
        self.Files.ENVIRONMENT = self.__set_file(
            f'{Conv.ENVIRONMENT_NAME_PREFIX}{self.__project_name}.tex' )
        self.Files.PROJECT_DEFINITION = self.__set_file(
            f'{Conv.PROJECT_NAME_PREFIX}{self.__project_name}.tex' )
        
        # make sure needed files exist
        self.create_default_environment()
        self.create_default_project_definition()
        
    def __set_root_folder( self, project_root_folder ):
        
        if not os.path.isdir( project_root_folder ):
            os.makedirs( project_root_folder )
        
        self.__project_root_folder = project_root_folder
        
    def get_root_folder( self ):
        return self.__project_root_folder
    
    def get_project_name( self ):
        return self.__project_name
    
    def __set_project_name( self, project_name ):
        
        # Private method, called once from constructor.
        
        if not project_name is None:
            # i provided custom project name
            self.__project_name = project_name
            return
            
        # i assume that root folder name is
        # the same as the project name
        
        basename = os.path.basename( self.__project_root_folder )
        #name, _ = os.path.splitext( basename )
        
        name = basename.replace( Conv.PROJECT_NAME_PREFIX, '' )
        
        self.__project_name = name
        
    def create_default_environment( self ):
        
        src = self.Files.ENVIRONMENT
        
        if os.path.isfile( src ):
            log.warning( f'file already exists: {src}, not doing anything' )
            return
        
        text = Conv.create_environment( self.__project_name )
        
        savef( src, text )
        
    def create_default_project_definition( self ):
        
        src = self.Files.PROJECT_DEFINITION
        
        if os.path.isfile( src ):
            log.warning( f'file already exists: {src}, not doing anything' )
            return
        
        text = Conv.create_project_definition( self.__project_name )
        
        savef( src, text )
        
    def __set_file( self, filename ):
        
        # Private method, called once from constructor.
        
        src = os.path.join(
            self.__project_root_folder,
            filename
            )
        
        return src
    
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
# end 2023.04.08
# created
