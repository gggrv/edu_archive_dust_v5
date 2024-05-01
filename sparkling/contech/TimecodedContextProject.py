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
from sparkling.contech.StandardContextProject import DStandardContextProject
from sparkling.contech.TimecodedContextConventions import (
    ConventionsTimecoded )
# other

class DTimecodedContextProject( DStandardContextProject ):
    
    # can and should be overridden
    Conventions = ConventionsTimecoded
    
    def __init__(
            self,
            project_root_folder,
            custom_conventions_class=None,
            ):
        
        # init project
        super( DTimecodedContextProject, self ).__init__( project_root_folder )
    
    def set_product_in_project( self, product_name_unprefixed=None, custom_template=None, is_timecoded=True ):
        c = self.Conventions
        prd_src = c.set_product_in_project( self.get_save_folder(), product_name_unprefixed=product_name_unprefixed, custom_template=self._get_template(custom_template), is_timecoded=is_timecoded )
        return super( DTimecodedContextProject, self )._set_product_in_project( prd_src )
        
    def set_component_in_product( self, product_root, component_name_unprefixed=None, custom_template=None, is_timecoded=True ):
        c = self.Conventions
        c_src = c.set_component_in_product( product_root, component_name_unprefixed=component_name_unprefixed, custom_template=self._get_template(custom_template), is_timecoded=is_timecoded )
        return super( DTimecodedContextProject, self )._set_component_in_product( c_src )
        
    def set_component_in_project( self, component_name_unprefixed=None, custom_template=None, is_timecoded=True ):
        c = self.Conventions
        c_src = c.set_component_in_project( self.get_save_folder(), component_name_unprefixed=component_name_unprefixed, custom_template=self._get_template(custom_template), is_timecoded=is_timecoded )
        return super( DTimecodedContextProject, self )._set_component_in_product( c_src )
    
#---------------------------------------------------------------------------+++
# end 2023.10.19
# simplified
