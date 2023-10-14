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
from sparkling.contech.SomeContextProject import SomeContextProject

BookNormal = SomeContextProject(
    'wawawa_BookNormal',
    custom_conventions_class=None
    )

BookTimecoded = SomeContextProject(
    'wawawa_BookTimecoded',
    custom_conventions_class=ConventionsTimecoded
    )

print()
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# created
