# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
# contech
from sparkling.contech.SomeContextProject import DSomeContextProject

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
        
    """
    def render_product( self, product, custom_context_console_command=None ):
        
        #unprefixed, prefixed = self.Conventions.get_correct_product_names( product, is_path=None )
        
        # get product src
        
        prd_src = None
        if product in self.__products:
            # i gave product name
            prd_src = self.__products[product]
        elif product is self.__products.values():
            # i gave product path
            prd_src = product
        elif os.path.isfile(product):
            # i gave product path
            prd_src = product
            log.warning( f'the product you want to render is not part of this project: {prd_src}' )
        else:
            # i gave something unknown
            raise ValueError( f'unknown product: {prd_src}' )
        
        # render it
        
        # TODO
        # allow custom commands
        return render_product( prd_src, context_console_command=custom_context_console_command )
    """
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
