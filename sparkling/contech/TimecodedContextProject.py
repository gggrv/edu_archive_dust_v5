# -*- coding: utf-8 -*-

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
