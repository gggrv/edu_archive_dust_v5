# -*- coding: utf-8 -*-
#BSD Zero Clause License
#
#Copyright (C) 2023 by Anna Anikina
#
#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted.
#
#THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#---------------------------------------------------------------------------+++

from sparkling.common.BaseColumns import BaseColumns

class CommandsStandard( BaseColumns ):
    
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
