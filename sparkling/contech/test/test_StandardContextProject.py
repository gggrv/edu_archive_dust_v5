# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.contech.StandardContextProject import DStandardContextProject, DSomeContextProject

try:
    ob  = DSomeContextProject( '' )
    raise NotImplementedError('AAAAAAAA')
except SyntaxError:
    print( 'ok' )

project_root = os.path.abspath( 'wawawa_BookNormal' )
BookNormal = DStandardContextProject(
    project_root,
    custom_conventions_class=None
    )

#BookTimecoded = SomeContextProject(
#    'wawawa_BookTimecoded',
#    custom_conventions_class=ConventionsTimecoded
#    )

BookNormal.set_project_in_project()
BookNormal.set_environment_in_project()
BookNormal.set_product_in_project( 'test_version' )
BookNormal.save_project_index()

index1 = BookNormal._project_index
BookNormal.load_project_index()
index2 = BookNormal._project_index

BookNormal.rebuild_project_index()
index3 = BookNormal._project_index

print()
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# created
