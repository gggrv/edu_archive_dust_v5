# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project

class Commands:
    
    # definitions
    ENVIRONMENT = r'\environment %environment_name%'
    ENVIRONMENT2 = r'\environment'
    PROJECT = r'\project %project_name%'
    PROJECT2 = r'\project'
    
    # imports
    COMPONENT = r'\component %component_name%'
    COMPONENT2 = r'\component'
    
    # start/stop
    
    STARTCOMPONENT = r'\startcomponent %component_name%'
    STARTCOMPONENT2 = r'\startcomponent'
    STOPCOMPONENT = r'\stopcomponent'
    
    STARTPRODUCT = r'\startproduct %product_name%'
    STARTPRODUCT2 = r'\startproduct'
    STOPPRODUCT = r'\stopproduct'
    
    # other
    
    REFERENCE = r'\reference[%value%]{%text%}'
    REFERENCE2 = r'\reference'
        
#---------------------------------------------------------------------------+++
# end 2023.05.19
# usability update
