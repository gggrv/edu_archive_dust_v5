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
