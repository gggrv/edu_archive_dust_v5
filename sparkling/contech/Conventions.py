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
from sparkling.common import readf

class Conventions:
    
    PROJECT_NAME_PREFIX = 'project_'
    ENVIRONMENT_NAME_PREFIX = 'env_'
    PRODUCT_NAME_PREFIX = 'prd_'
    COMPONENT_NAME_PREFIX = 'c_'
    
    class Files:
        
        ENVIROMENT = 'env_.tex'
        PROJECT_DEFINITION = 'project_.tex'
        
    @staticmethod
    def create_environment( project_name ):
        
        src = Conventions.Files.ENVIRONMENT
        
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
    def create_project_definition( project_name ):
        
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

#---------------------------------------------------------------------------+++
# end 2023.04.08
# created
