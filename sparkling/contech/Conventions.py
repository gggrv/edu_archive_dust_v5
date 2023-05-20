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

class Conventions:
    
    PROJECT_NAME_PREFIX = 'project_'
    ENVIRONMENT_NAME_PREFIX = 'env_'
    PRODUCT_NAME_PREFIX = 'prd_'
    COMPONENT_NAME_PREFIX = 'c_'
    
    class Folders:
        
        IMAGES = 'images' # same as the one in the default environment definition file
    
    class Files:
        
        ENVIROMENT_DEFINITION = 'env_.tex'
        PROJECT_DEFINITION = 'project_.tex'
        
    @staticmethod
    def default_environment_definition( project_name ):
        
        # Creates the environment file contents.
        
        src = Conventions.Files.ENVIROMENT_DEFINITION
        
        if not os.path.isfile( src ):
            log.error( f'no default template for environment: {src}' )
            return f'%missing template {src}'
        
        environment_name = f'{Conventions.ENVIRONMENT_NAME_PREFIX}{project_name}'
        prefixed_project_name = f'{Conventions.PROJECT_NAME_PREFIX}{project_name}'
        
        text = readf( src )
        text = text.replace( '%environment_name%', environment_name )
        text = text.replace( '%project_name%', prefixed_project_name )
        
        return text
        
    @staticmethod
    def default_project_definition( project_name ):
        
        # Creates the project file contents.
        
        src = Conventions.Files.PROJECT_DEFINITION
        
        if not os.path.isfile( src ):
            log.error( f'no default template for project definition: {src}' )
            return f'%missing template {src}'
        
        environment_name = f'{Conventions.ENVIRONMENT_NAME_PREFIX}{project_name}'
        prefixed_project_name = f'{Conventions.PROJECT_NAME_PREFIX}{project_name}'
        
        text = readf( src )
        text = text.replace( '%environment_name%', environment_name )
        text = text.replace( '%project_name%', prefixed_project_name )
        
        return text
    
    @staticmethod
    def create_project( path_to_new_project ):
        
        # Treats given path as a project root.
        # Creates necessary definitions, folders.
        
        # get project name
        project_name = os.path.basename( path_to_new_project )
        
        # create necessary folders
        for folder in Conventions.Folders.SAMPLE_PROJECT_FOLDERS:
            src = os.path.join( path_to_new_project, folder )
            os.makedirs( src )
            
        # populate folders with necessary files
        
        # project
        src = os.path.join( path_to_new_project, Conventions.Files.PROJECT_DEFINITION )
        text = Conventions.default_project_definition( project_name )
        savef( src, text )

        # environment
        src = os.path.join( path_to_new_project, Conventions.Files.ENVIROMENT_DEFINITION )
        text = Conventions.default_environment_definition( project_name )
        savef( src, text )
        
#---------------------------------------------------------------------------+++
# end 2023.05.19
# usability update
