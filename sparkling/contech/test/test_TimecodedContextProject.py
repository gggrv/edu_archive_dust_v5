# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.contech.TimecodedContextProject import DTimecodedContextProject

project_root = os.path.abspath( 'wawawa_BookTimecoded' )
Book = DTimecodedContextProject(
    project_root,
    custom_conventions_class=None
    )

Book.set_project_in_project()
Book.set_environment_in_project()
Book.set_product_in_project()
prd_root = os.path.dirname( Book.set_product_in_project( 'uncoded', is_timecoded=False ) )
Book.set_component_in_project()
Book.set_component_in_project( '20200101' )
Book.set_component_in_product( prd_root, 'eeeeeee', is_timecoded=False)
Book.save_project_index()

index1 = Book._project_index
Book.load_project_index()
index2 = Book._project_index

Book.rebuild_project_index()
index3 = Book._project_index

print()
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# created
