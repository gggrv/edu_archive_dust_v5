# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.contech.TimecodedContextConventions import ConventionsTimecoded

c = ConventionsTimecoded

# start here
project_root = r'wawawaTimecodedBook'

# create folder
project_root = c.set_project( project_root )

# necessary files
env = c.set_environment_in_project( project_root )
project_definition = c.set_project_in_project( project_root )

# first product
prd_test = c.set_product_in_project( project_root )
product_root = os.path.dirname( prd_test )
cs = [ c.set_component_in_product( product_root ) for iloc in range(5) ]

# second product
prd_2 = c.set_product_in_project( project_root, product_name_unprefixed='202401' )
product_root2 = os.path.dirname( prd_2 )
cs = [ c.set_component_in_product( product_root, component_name_unprefixed=f'202401{iloc}' ) for iloc in range(10,15) ]

# alternative product
#project_name_unprefixed, _ = c.get_correct_project_names( project_root, True )
#prd_alter = c.set_product_in_product( product_root, project_name_unprefixed )

# alternative env
env_alter = c.set_environment_in_project( project_root, 'AAAAAAA' )

print()
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
