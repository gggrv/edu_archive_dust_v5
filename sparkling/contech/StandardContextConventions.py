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
from sparkling.common import readf, savef
from sparkling.common.BaseColumns import BaseColumns

def _path2str( text, is_path ):
    
    # Specialised funtion that may safely convert
    # given path to string.
    
    if is_path is False:
        # this is a string and i know it already
        return text
    
    # doesn't matter
    return os.path.splitext( os.path.basename(text) )[0]

def _get_correct_names( name, prefix, is_path ):
    
    # Parses `name`. `is_path` may be:
    # - None (don't know)
    # - False (definitely not a path)
    # - True (definitely is a path)
    
    name = _path2str( name, is_path )
    
    unprefixed = name
    prefixed = name
    
    # make sure it is prefixed
    if not prefixed.startswith( prefix ):
        prefixed = prefix + prefixed.replace(prefix,'')
        
    # make sure it is unprefixed
    if prefix in unprefixed:
        unprefixed = unprefixed.replace(prefix,'')
        
    return unprefixed, prefixed

def folder_name_corresponds_to_value( root_folder, prefixed_name ):
    
    # Tests whether given `root folder` actually
    # corresponds to given `prefixed name`.
    
    basename = os.path.basename( root_folder )
    return basename == prefixed_name

class ConventionsStandard( BaseColumns ):
    
    # These conventions attempt to follow
    # the ones described here:
    # https://wiki.contextgarden.net/Project_structure
    
    PROJECT_NAME_PREFIX = 'project_'
    ENVIRONMENT_NAME_PREFIX = 'env_'
    PRODUCT_NAME_PREFIX = 'prd_'
    COMPONENT_NAME_PREFIX = 'c_'
    DOT_EXT = '.tex'
    
    _path2str = staticmethod( _path2str )
    
    class Folders( BaseColumns ):
        
        # i have some templates from which
        # custom files can be made
        TEMPLATES = os.path.dirname(__file__)
        
        # folder name that i will paste into the `environment`
        # where will the context look for images relative
        # to any product
        IMAGES = 'images'
    
    class Files( BaseColumns ):
        ENVIRONMENT_FILE_TEMPLATE = 'env_.tex'
        PROJECT_FILE_TEMPLATE = 'project_.tex'
        PRODUCT_FILE_TEMPLATE = 'prd_.tex'
        COMPONENT_FILE_TEMPLATE = 'c_.tex'
        
    @classmethod
    def get_correct_project_names( cls, project_name, is_path ):
        return _get_correct_names( project_name, cls.PROJECT_NAME_PREFIX, is_path )
    @classmethod
    def get_correct_environment_names( cls, environment_name, is_path ):
        return _get_correct_names( environment_name, cls.ENVIRONMENT_NAME_PREFIX, is_path )
    @classmethod
    def get_correct_product_names( cls, product_name, is_path ):
        return _get_correct_names( product_name, cls.PRODUCT_NAME_PREFIX, is_path )
    @classmethod
    def get_correct_component_names( cls, component_name, is_path ):
        return _get_correct_names( component_name, cls.COMPONENT_NAME_PREFIX, is_path )
        
    @classmethod
    def project_root_is_valid( cls, project_root ):
        basename = os.path.basename( project_root )
        unprefixed, prefixed = cls.get_correct_project_names( project_root, True )
        return prefixed==basename
        #if not cls.project_root_is_valid( project_root ):
        #    raise NameError( f'please include {cls.PROJECT_NAME_PREFIX} in the project directory name, not doing anything' )
    
    @classmethod
    def __get_template( cls, template_name, read_contents=True, custom_template=None ):
        
        # For internal use only.
        
        if not custom_template is None:
            # i want custom data
            if read_contents:
                return readf( custom_template )
            return custom_template
        
        # i want default data
        
        src = os.path.join( cls.Folders.TEMPLATES, template_name )
        if not read_contents:
            return src
        
        if not os.path.isfile( src ):
            log.error( f'no default template for environment: {src}' )
            return
        
        return readf( src )
    
    @classmethod
    def __generate_environment_file_definition( cls,
        src,
        project_name_unprefixed, custom_env_name_unprefixed=None,
        custom_template=None ):
        
        # Writes the environment file contents.
        
        text = cls.__get_template( cls.Files.ENVIRONMENT_FILE_TEMPLATE, custom_template=custom_template )
        if text is None:
            savef( src, '% missing template' )
            return
        
        env_name_unprefixed = project_name_unprefixed if custom_env_name_unprefixed is None else custom_env_name_unprefixed
        environment_name_prefixed = f'{cls.ENVIRONMENT_NAME_PREFIX}{env_name_unprefixed}'
        project_name_prefixed = f'{cls.PROJECT_NAME_PREFIX}{project_name_unprefixed}'
        
        text = text.replace( '%environment_name_prefixed%', environment_name_prefixed )
        text = text.replace( '%project_name_prefixed%', project_name_prefixed )
        text = text.replace( '%images%', cls.Folders.IMAGES )
        
        savef( src, text )
        
    @classmethod
    def _generate_project_file_definition( cls, src, project_name_unprefixed, custom_template=None ):
        
        # Writes the project file contents.
        
        text = cls.__get_template( cls.Files.PROJECT_FILE_TEMPLATE, custom_template=custom_template )
        if text is None:
            savef( src, '% missing template' )
            return
        
        environment_name = f'{cls.ENVIRONMENT_NAME_PREFIX}{project_name_unprefixed}'
        project_name_prefixed = f'{cls.PROJECT_NAME_PREFIX}{project_name_unprefixed}'
        
        text = text.replace( '%environment_name_prefixed%', environment_name )
        text = text.replace( '%project_name_prefixed%', project_name_prefixed )
        savef( src, text )
        
    @classmethod
    def _generate_product_file_definition( cls, src, project_name_unprefixed, product_name_unprefixed, custom_template=None ):
        
        # Writes the product file contents.
        
        text = cls.__get_template( cls.Files.PRODUCT_FILE_TEMPLATE, custom_template=custom_template )
        if text is None:
            savef( src, '% missing template' )
            return
        
        environment_name_prefixed = f'{cls.ENVIRONMENT_NAME_PREFIX}{project_name_unprefixed}'
        project_name_prefixed = f'{cls.PROJECT_NAME_PREFIX}{project_name_unprefixed}'
        product_name_prefixed = f'{cls.PRODUCT_NAME_PREFIX}{product_name_unprefixed}'
        
        text = text.replace( '%product_name_prefixed%', product_name_prefixed )
        text = text.replace( '%environment_name_prefixed%', environment_name_prefixed )
        text = text.replace( '%project_name_prefixed%', project_name_prefixed )
        savef( src, text )
        
    @classmethod
    def _generate_component_file_definition( cls,
        src, component_name_unprefixed, custom_template=None ):
            
        # Writes the component file contents.
        
        # This function allows me to create a verbose
        # `component`.
        
        # It is inconvenient to have so much
        # useless data - `components` work
        # perfectly fine even when they are completely empty.
        
        # This function exists for completeness and
        # is usually overridden by a bit more relaxed conventions.
        
        # According to standard conventions, I could also add
        # `product name` into `component`.
        # I don't do this to avoid confusion:
        # multiple `prd.tex` files can exist in the same `product root`.
        # This `component` belongs to any/all of them.
        
        text = cls.__get_template( cls.Files.COMPONENT_FILE_TEMPLATE, custom_template=custom_template )
        if text is None:
            savef( src, '% missing template' )
            return
        
        component_name_prefixed = f'{cls.COMPONENT_NAME_PREFIX}{component_name_unprefixed}'
        
        text = text.replace( '%component_name_prefixed%', component_name_prefixed )
        savef( src, text )
    
    @classmethod
    def set_project( cls, project_root ):
        
        # Sets valid project folder.
        # Logically similar to `SomeDoer.set_folder(...)`, but
        # actually changes folder name to the correct one if needed.
        
        # get correct names
        project_unprefixed, project_prefixed = cls.get_correct_project_names( project_root, True )
        
        correct_project_root = os.path.join( os.path.dirname(project_root), project_prefixed )
        if not os.path.isdir( correct_project_root ):
            os.makedirs( correct_project_root )
            
        return correct_project_root
            
    @classmethod
    def set_project_in_project( cls,
        project_root,
        custom_template=None ):

        # Creates `project definition file` in a given
        # project folder.
        # Only one `project definition file` should exist
        # for each `project folder`.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        # get correct names
        project_unprefixed, project_prefixed = cls.get_correct_project_names( project_root, True )
        
        project_src = os.path.join( project_root, f'{project_prefixed}{cls.DOT_EXT}' )
        cls._generate_project_file_definition( project_src, project_unprefixed, custom_template=custom_template )
        return project_src
            
    @classmethod
    def set_environment_in_project( cls,
        project_root,
        env_name_unprefixed=None,
        custom_template=None ):

        # Creates `environment file` in a given
        # project folder.
        # Usually only one env exists in a project,
        # but I may want to have multiple ones
        # and switch between them.
        # This is why creating differently-named env files is possible.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        # I want to have this environment in project.
        #   ■ `project_something`
        #   ├─■ `env_something` <- i want this file to exist
        #   └─■ anything else
        
        # get correct names
        project_unprefixed, project_prefixed = cls.get_correct_project_names( project_root, True )
        env_name_unprefixed, env_name_prefixed = cls.get_correct_environment_names( project_unprefixed, False ) \
            if env_name_unprefixed is None \
            else cls.get_correct_environment_names( env_name_unprefixed, False )
        
        # make sure appropriate folder exists
        if not os.path.isdir( project_root ):
            os.makedirs( project_root )
            
        # make sure file exists
        env_src = os.path.join( project_root, f'{env_name_prefixed}{cls.DOT_EXT}' )
        if not os.path.isfile(env_src):
            # create default one
            cls.__generate_environment_file_definition( env_src, project_unprefixed, custom_env_name_unprefixed=env_name_unprefixed, custom_template=custom_template )
        
        return env_src
        
    @classmethod
    def set_product_in_project( cls,
        project_root,
        product_name_unprefixed,
        custom_template=None ):
        
        # Multiple unique products can exist in
        # project.
        # Each product has access only to it's own
        # components.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        # I want to have this product in project.
        #   ■ `project_something`
        #   └─■ `prd_something` <- i want this folder to exist
        #     ├─■ `prd_definition` <- i want this file to exist
        #     └─■ anything else <- does not matter
        
        # get correct names
        project_unprefixed, project_prefixed = cls.get_correct_project_names( project_root, True )
        _, product_name_prefixed = cls.get_correct_product_names( product_name_unprefixed, False )
        
        # make sure appropriate folder exists
        prd_root = os.path.join( project_root, product_name_prefixed )
        if not os.path.isdir( prd_root ):
            os.makedirs( prd_root )
            
        # make sure file exists
        prd_src = os.path.join( prd_root, f'{product_name_prefixed}{cls.DOT_EXT}' )
        if not os.path.isfile(prd_src):
            # create default one
            cls._generate_product_file_definition( prd_src, project_unprefixed, product_name_unprefixed, custom_template=custom_template )
        
        return prd_src
        
    @classmethod
    def set_product_in_product( cls,
        existing_product_root,
        project_name_unprefixed,
        product_name_unprefixed,
        custom_template=None ):
            
        # I may want to have several variations of the
        # same product. This means that all these variations
        # have access to same components - all these variations
        # are located in the same folder. Computers don't allow
        # to have multiple identically-named files in the
        # same folder, so I have to supply custom `product_name_unprefixed`
        # for this `new` product.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        # I want to have this product in another product folder.
        # This way the `new product` will be able to access
        # components of the `old product`.
        #   ■ `project_something`
        #   └─■ `prd_something` <- it most likely already exists
        #     ├─■ `prd_definition1` <- it most likely already exists
        #     ├─■ `prd_definition2` <- i want this file to exist
        #     └─■ anything else <- does not matter
        
        # get correct names
        _, project_name_prefixed = cls.get_correct_project_names( project_name_unprefixed, False )
        _, product_name_prefixed = cls.get_correct_product_names( product_name_unprefixed, False )
        
        # make sure appropriate folder exists
        if not os.path.isdir( existing_product_root ):
            os.makedirs( existing_product_root )
            
        # make sure file exists
        prd_src = os.path.join( existing_product_root, f'{product_name_prefixed}{cls.DOT_EXT}' )
        if not os.path.isfile(prd_src):
            # create default one
            cls._generate_product_file_definition( prd_src, project_name_unprefixed, product_name_unprefixed, custom_template=custom_template )
        
        return prd_src
        
    @classmethod
    def set_component_in_product( cls,
        product_root,
        component_name_unprefixed,
        custom_template=None ):
        
        # Multiple components may exist in one product.
        # I don't want to automatically add this `component` into `prd`,
        # because:
        # - `prd.tex` are usually manually managed by a human
        # - there may be multiple alternative `prd.tex` in this `product_root`, no idea which one to choose.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        # I want to have this component in product.
        #   ■ `project_something`
        #   └─■ `prd_something` <- exists
        #     ├─■ `prd_definition` <- does not matter
        #     ├─■ `c_definition` <- i want this file to exist
        #     └─■ anything else <- does not matter
        
        # get correct names
        _, component_name_prefixed = cls.get_correct_component_names( component_name_unprefixed, False )
        
        # make sure appropriate folder exists
        if not os.path.isdir( product_root ):
            os.makedirs( product_root )
            
        # make sure file exists
        c_src = os.path.join( product_root, f'{component_name_prefixed}{cls.DOT_EXT}' )
        if not os.path.isfile(c_src):
            # create default one
            cls._generate_component_file_definition( c_src, component_name_unprefixed, custom_template=custom_template )
        
        return c_src
        
    @classmethod
    def set_component_in_autoproduct( cls,
        autoproduct_root,
        component_name_unprefixed,
        custom_template=None ):
        
        # I want to automatically add this `component` into `prd`.
        # Target `prd` is created and deleted automatically.
        # Any human labor dedicated to that `prd` will be ignored and lost.
        
        # Logically similar to `SomeDoer.set_file(...)`, but actually
        # creates this file if needed.
        
        raise NotImplementedError
        
    @classmethod
    def switch_environment( cls ):
        
        # for `project file`
        # for specific `product`
    
        raise NotImplementedError
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# created
