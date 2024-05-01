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
from sparkling.contech.StandardContextConventions import ConventionsStandard

c = ConventionsStandard

# start here
project_root = r'wawawa_test_book'

# create folder
project_root = c.set_project( project_root )

# necessary files
env = c.set_environment_in_project( project_root )
project_definition = c.set_project_in_project( project_root )

# first product
prd_test = c.set_product_in_project( project_root, 'test' )
product_root = os.path.dirname( prd_test )
cs = [ c.set_component_in_product( product_root, str(iloc) ) for iloc in range(5) ]

# alternative product
project_name_unprefixed, _ = c.get_correct_project_names( project_root, True )
prd_alter = c.set_product_in_product( product_root, project_name_unprefixed, 'eeeeeee' )

# alternative env
env_alter = c.set_environment_in_project( project_root, 'AAAAAAA' )

print()
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
