# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import datetime as dt
import os
# pip install
# same project
from sparkling.contech.StandardContextConventions import ConventionsStandard

PRODUCT_DT_FORMAT = '%Y%m'
COMPONENT_DT_FORMAT = '%Y%m%d'

def _validate_unprefixed_name( name, custom_format ):
    dt.datetime.strptime( name, custom_format )
    return name
    
def new_unprefixed_name( custom_format, datetime=None ):
    datetime = dt.datetime.now() if datetime is None else datetime
    return datetime.strftime( custom_format )

class ConventionsTimecoded( ConventionsStandard ):
    
    # These conventions are very similar to the standard ones.
    # Notable differences:
    # components don't have prefixes.
    # Product and component names are generated automatically
    # based on current datetime.
    
    COMPONENT_NAME_PREFIX = ''
    
    @classmethod
    def set_product_in_project( cls,
        project_root,
        product_name_unprefixed=None,
        custom_template=None ):
        
        # get correct product name
        unprefixed = new_unprefixed_name(PRODUCT_DT_FORMAT) if product_name_unprefixed is None else _validate_unprefixed_name(product_name_unprefixed,PRODUCT_DT_FORMAT)
        
        return ConventionsStandard.set_product_in_project( project_root, unprefixed, custom_template=custom_template )
        
    @classmethod
    def set_product_in_product( cls,
        existing_product_root,
        project_name_unprefixed,
        product_name_unprefixed,
        custom_template=None ):
        
        raise NotImplementedError
        
    @classmethod
    def set_component_in_product( cls,
        product_root,
        component_name_unprefixed=None,
        custom_template=None ):
        
        # get correct component name
        unprefixed = new_unprefixed_name(COMPONENT_DT_FORMAT) if component_name_unprefixed is None else _validate_unprefixed_name(component_name_unprefixed,COMPONENT_DT_FORMAT)
        
        # fix product name so it corresponds to chosen component name
        datetime = dt.datetime.strptime( unprefixed, COMPONENT_DT_FORMAT )
        expected_basename = datetime.strftime( PRODUCT_DT_FORMAT )
        root, basename = os.path.split( product_root )
        if not basename == expected_basename:
            _,product_prefixed = cls.get_correct_product_names( expected_basename, False )
            product_root = os.path.join( root, product_prefixed )
        
        return ConventionsStandard.set_component_in_product( product_root, unprefixed, custom_template=custom_template )
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
