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
