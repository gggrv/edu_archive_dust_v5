# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.common.SomeDoer import SomeDoer
# contech
from sparkling.contech.StandardContextConventions import ConventionsStandard

class SomeContextProject( SomeDoer ):
    
    # Custom doer that
    # gives easy access to any `ConTeXt` project.
    # Assumes that the project follows specific `conventions`.
    
    # can and should be overridden
    Conventions = ConventionsStandard
    
    def __init__(
            self,
            project_root_folder,
            custom_conventions_class=None,
            ):
        
        # override conventions
        if not custom_conventions_class is None:
            self.Conventions = custom_conventions_class
        # short name for convenience
        c = self.Conventions
        
        # set save folder
        project_root_folder = c.set_project(project_root_folder)
        super( SomeContextProject, self ).__init__( project_root_folder )
        
        # paths
    
    def get_correct_project_names( self ):
        return self.Conventions.get_correct_project_names( self.get_save_folder(), True )
    
    """
    def generate_missing_files( self ):
        
        c = self.Conventions
        
        src = self.Files.ENVIRONMENT
        if not os.path.isfile( src ):
            c.generate_environment_file_definition( src, self.__project_name_unprefixed )
                
        src = self.Files.PROJECT
        if not os.path.isfile( src ):
            c.generate_project_file_definition( src, self.__project_name_unprefixed )
    
    def products( self, rescan=False ):
        
        # Finds and saves existing `product definitions`
        # into memory.
        
        if len( self.__products )==0 or rescan:
            # need to rescan
            
            prd_srcs = get_existing_products( self.__project_root_folder, prefix=self.Conventions.PRODUCT_NAME_PREFIX )
            
            found = {}
            for prd_src in prd_srcs:
                unprefixed, prefixed = self.Conventions.get_correct_product_names( prd_src, is_path=True )
                found[ unprefixed ] = prd_src
                
            self.__products = found
            
        # ok
        return self.__products
    
    def render_product( self, product, custom_context_console_command=None ):
        
        #unprefixed, prefixed = self.Conventions.get_correct_product_names( product, is_path=None )
        
        # get product src
        
        prd_src = None
        if product in self.__products:
            # i gave product name
            prd_src = self.__products[product]
        elif product is self.__products.values():
            # i gave product path
            prd_src = product
        elif os.path.isfile(product):
            # i gave product path
            prd_src = product
            log.warning( f'the product you want to render is not part of this project: {prd_src}' )
        else:
            # i gave something unknown
            raise ValueError( f'unknown product: {prd_src}' )
        
        # render it
        
        # TODO
        # allow custom commands
        return render_product( prd_src, context_console_command=custom_context_console_command )
    """
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
