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
from sparkling.contech.StandardContextConventions import (
    ConventionsStandard, BaseColumns )
from sparkling.contech.main import (
    get_existing_products, get_existing_components,
    get_existing_environments
    )
# other
from sparkling.common import readf_yaml, savef_yaml

class ColumnsProjectIndex( BaseColumns ):
    
    # This is an interface to a custom `.yaml` file that records
    # contents of a `ConTeXt` project.
    # This allows to avoid disk scanning when files
    # are created programmatically.
    # All recorded paths will be relative to the `project root`.
    # Expected `index` structure:
    # ---
    # PROJECT_DEFINITION: src1
    # ENVIRONMENTS: [src1,src2,src3]
    # PRODUCTS: [src1,src2,src3]
    # COMPONENTS: [src1,src2,src3]
    # ...
    
    PROJECT_DEFINITION = 'project_definition'
    ENVIRONMENTS = 'environments'
    PRODUCTS = 'products'
    COMPONENTS = 'components'
    
    @classmethod
    def _set_multivalue( cls, column, index, src ):
        
        # foolcheck
        if not type(src) == str:
            raise ValueError
        
        if column in index:
            index[column].append( src )
            return

        index[column] = [ src ]
        
    @classmethod
    def _set_multivalues( cls, column, index, srcs ):
        
        # foolcheck
        if type(srcs) == str:
            raise ValueError
            
        if column in index:
            index[column].extend( srcs )
            return

        index[column] = srcs
    
    @classmethod
    def set_project_definition( cls, index, src ):
        index[ cls.PROJECT_DEFINITION ] = src
        
    @classmethod
    def set_environment( cls, index, src ):
        cls._set_multivalue( cls.ENVIRONMENTS, index, src )
    @classmethod
    def set_environments( cls, index, srcs ):
        cls._set_multivalues( cls.ENVIRONMENTS, index, srcs )

    @classmethod
    def set_product( cls, index, src ):
        cls._set_multivalue( cls.PRODUCTS, index, src )
    @classmethod
    def set_products( cls, index, srcs ):
        cls._set_multivalues( cls.PRODUCTS, index, srcs )

    @classmethod
    def set_component( cls, index, src ):
        
        # remove prodcuts
        if cls.PRODUCTS in index:
            if src in index[cls.PRODUCTS]:
                return
            
        cls._set_multivalue( cls.COMPONENTS, index, src )
        
    @classmethod
    def set_components( cls, index, srcs ):
        
        ok = []
        
        # remove prodcuts
        if cls.PRODUCTS in index:
            [ ok.append(src) for src in srcs if not src in index[cls.PRODUCTS] ]
        
        cls._set_multivalues( cls.COMPONENTS, index, ok )

class SomeContextProject( SomeDoer ):
    
    # Custom doer that
    # gives easy access to any `ConTeXt` project.
    # Assumes that the project follows specific `conventions`.
    
    # can and should be overridden
    Conventions = ConventionsStandard
    
    # in order to avoid disk scanning, i will be recording
    # all items relevant to this project in this `index`
    # future dictionary
    _project_index = None
    
    class Files:
        PROJECT_INDEX = 'project_index.yaml'
        
    class Folders:
        CONTEXT_TEMPLATES = 'context_templates'
    
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
        self.Folders.CONTEXT_TEMPLATES = self.set_folder( self.Folders.CONTEXT_TEMPLATES )
        self.Files.PROJECT_INDEX = self.set_file( self.Files.PROJECT_INDEX )
        
        # other
        self._project_index = {}
    
    def get_correct_project_names( self ):
        # For external use only.
        return self.Conventions.get_correct_project_names( self.get_save_folder(), True )
            
    def __get_template( self, template_filename ):
        
        # For internal use only.
        # Creates the `custom_template` value that can be passed
        # to `Conventions`.
        
        if template_filename is None:
            return
        
        src = os.path.join( self.Folders.CONTEXT_TEMPLATES, template_filename )
        return src
    
    def set_project_in_project( self, custom_template=None ):
        c = self.Conventions
        project_src = c.set_project_in_project( self.get_save_folder(), custom_template=self.__get_template(custom_template) )
        project_src = os.path.relpath( project_src, self.get_save_folder() )
        ColumnsProjectIndex.set_project_definition( self._project_index, project_src )
            
    def set_environment_in_project( self, env_name_unprefixed=None, custom_template=None ):
        c = self.Conventions
        env_src = c.set_environment_in_project( self.get_save_folder(), env_name_unprefixed=env_name_unprefixed, custom_template=self.__get_template(custom_template) )
        env_src = os.path.relpath( env_src, self.get_save_folder() )
        ColumnsProjectIndex.set_environment( self._project_index, env_src )
        
    def set_product_in_project( self, product_name_unprefixed, custom_template=None ):
        c = self.Conventions
        prd_src = c.set_product_in_project( self.get_save_folder(), product_name_unprefixed, custom_template=self.__get_template(custom_template) )
        prd_src = os.path.relpath( prd_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, prd_src )
        
    def set_product_in_product( self, existing_product_root, product_name_unprefixed, custom_template=None ):
        c = self.Conventions
        project_unprefixed, _ = c.get_correct_project_names( self.get_save_folder(), True )
        prd_src = c.set_product_in_product( existing_product_root, project_unprefixed, product_name_unprefixed, custom_template=self.__get_template(custom_template) )
        prd_src = os.path.relpath( prd_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, prd_src )
        
    def set_component_in_product( self, product_root, component_name_unprefixed, custom_template=None ):
        c = self.Conventions
        c_src = c.set_component_in_product( product_root, component_name_unprefixed, custom_template=self.__get_template(custom_template) )
        c_src = os.path.relpath( c_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, c_src )
        
    def save_project_index( self ):
        savef_yaml( self.Files.PROJECT_INDEX, self._project_index )
        
    def load_project_index( self ):
        self._project_index = readf_yaml( self.Files.PROJECT_INDEX )
        
    def rebuild_project_index( self ):
        
        # Fully rescans project folder and
        # replaces current `project index` with
        # real-life up-to-date data.
        
        # reset existing
        self._project_index = {}
        
        # project definition
        self.set_project_in_project()
        
        # environments
        src = get_existing_environments( self.get_save_folder(), prefix=self.Conventions.ENVIRONMENT_NAME_PREFIX )
        ColumnsProjectIndex.set_environments( self._project_index, src )
        
        # products
        src = get_existing_products( self.get_save_folder(), prefix=self.Conventions.PRODUCT_NAME_PREFIX )
        ColumnsProjectIndex.set_products( self._project_index, src )
        
        # components
        src = get_existing_products( self.get_save_folder(), prefix=self.Conventions.PRODUCT_NAME_PREFIX )
        ColumnsProjectIndex.set_components( self._project_index, src )
        
        self.save_project_index()
        
    """
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
