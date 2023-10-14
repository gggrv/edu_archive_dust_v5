# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

from sparkling.common.BaseColumns import BaseColumns

class ContextCommands( BaseColumns ):
    
    # definitions
    environment_named = r'\environment %environment_name%'
    environment = r'\environment'
    project_named = r'\project %project_name%'
    project = r'\project'
    
    # imports
    component_named = r'\component %component_name%'
    component = r'\component'
    
    # start/stop
    
    start_component_named = r'\startcomponent %component_name%'
    start_component = r'\startcomponent'
    stop_component = r'\stopcomponent'
    
    start_product_named = r'\startproduct %product_name%'
    start_product = r'\startproduct'
    stop_product = r'\stopproduct'
    
    # other
    
    reference_with_value = r'\reference[%value%]{%text%}'
    reference = r'\reference'
    
    # console
    
    console_render_product = '%path_to_context% %product_name%'
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
