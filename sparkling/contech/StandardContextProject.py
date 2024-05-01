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

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
# contech
from sparkling.contech.SomeContextProject import DSomeContextProject
from sparkling.contech.main import render_product

class DStandardContextProject( DSomeContextProject ):
    
    def __init__(
            self,
            project_root_folder,
            custom_conventions_class=None,
            ):
        
        # init project
        super( DStandardContextProject, self ).__init__( project_root_folder )
    
    def set_project_in_project( self, custom_template=None ):
        c = self.Conventions
        project_src = c.set_project_in_project( self.get_save_folder(), custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_project_in_project( project_src )
            
    def set_environment_in_project( self, env_name_unprefixed=None, custom_template=None ):
        c = self.Conventions
        env_src = c.set_environment_in_project( self.get_save_folder(), env_name_unprefixed=env_name_unprefixed, custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_environment_in_project( env_src )
        
    def set_product_in_project( self, product_name_unprefixed, custom_template=None ):
        c = self.Conventions
        prd_src = c.set_product_in_project( self.get_save_folder(), product_name_unprefixed, custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_product_in_project( prd_src )
        
    def set_product_in_product( self, existing_product_root, product_name_unprefixed, custom_template=None ):
        c = self.Conventions
        project_unprefixed, _ = c.get_correct_project_names( self.get_save_folder(), True )
        prd_src = c.set_product_in_product( existing_product_root, project_unprefixed, product_name_unprefixed, custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_product_in_product( prd_src )
        
    def set_component_in_product( self, product_root, component_name_unprefixed, custom_template=None ):
        c = self.Conventions
        c_src = c.set_component_in_product( product_root, component_name_unprefixed, custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_component_in_product( c_src )
       
    def render_product( self, prd_src, custom_context_console_command='context' ):
        
        # TODO
        # allow custom commands
        return render_product( prd_src, context_console_command=custom_context_console_command )
    
#---------------------------------------------------------------------------+++
# end 2023.10.19
# enabled `render_product`
