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

class DSomeContextProject( SomeDoer ):
    
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
        super( DSomeContextProject, self ).__init__( project_root_folder )
        
        # paths
        self.Folders.CONTEXT_TEMPLATES = self.set_folder( self.Folders.CONTEXT_TEMPLATES )
        self.Files.PROJECT_INDEX = self.set_file( self.Files.PROJECT_INDEX )
        
        # other
        self._project_index = {}
    
    def __new__( cls, *args, **kwargs ):
        
        # This class should never be instantiated - only subclasses.
        
        # help:
        # https://stackoverflow.com/questions/7989042/preventing-a-class-from-direct-instantiation-in-python
        if cls is DSomeContextProject:
            raise SyntaxError( 'this class is virtual - subclass it in order to create instances' )
            
        return super().__new__( cls )
        
    def get_correct_project_names( self ):
        # For external use only.
        return self.Conventions.get_correct_project_names( self.get_save_folder(), True )
            
    def _get_template( self, template_filename ):
        
        # For internal use only.
        # Creates the `custom_template` value that can be passed
        # to `Conventions`.
        
        if template_filename is None:
            return
        
        src = os.path.join( self.Folders.CONTEXT_TEMPLATES, template_filename )
        return src
    
    def _set_project_in_project( self, project_src ):
        src = os.path.relpath( project_src, self.get_save_folder() )
        ColumnsProjectIndex.set_project_definition( self._project_index, src )
        return project_src
            
    def _set_environment_in_project( self, env_src ):
        src = os.path.relpath( env_src, self.get_save_folder() )
        ColumnsProjectIndex.set_environment( self._project_index, src )
        return env_src
        
    def _set_product_in_project( self, prd_src ):
        src = os.path.relpath( prd_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, src )
        return prd_src
        
    def _set_product_in_product( self, prd_src ):
        src = os.path.relpath( prd_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, src )
        return prd_src
        
    def _set_component_in_product( self, c_src ):
        src = os.path.relpath( c_src, self.get_save_folder() )
        ColumnsProjectIndex.set_product( self._project_index, src )
        return c_src
        
    def save_project_index( self ):
        savef_yaml( self.Files.PROJECT_INDEX, self._project_index )
        
    def load_project_index( self ):
        self._project_index = readf_yaml( self.Files.PROJECT_INDEX )
        
    def rebuild_project_index( self, save=True ):
        
        # Fully rescans project folder and
        # replaces current `project index` with
        # real-life up-to-date data.
        
        c = self.Conventions
        
        # reset existing
        self._project_index = {}
        
        # project definition
        self.set_project_in_project()
        
        # environments
        src = get_existing_environments( self.get_save_folder(), prefix=c.ENVIRONMENT_NAME_PREFIX, relpath=True )
        ColumnsProjectIndex.set_environments( self._project_index, src )
        
        # products
        src = get_existing_products( self.get_save_folder(), prefix=c.PRODUCT_NAME_PREFIX, relpath=True )
        ColumnsProjectIndex.set_products( self._project_index, src )
        
        # components
        src = get_existing_components( self.get_save_folder(), True, prefix=c.COMPONENT_NAME_PREFIX, relpath=True )
        ColumnsProjectIndex.set_components( self._project_index, src )
        
        if save:
            self.save_project_index()
    
#---------------------------------------------------------------------------+++
# end 2023.10.19
# moved here
