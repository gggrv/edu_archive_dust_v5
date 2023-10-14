# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

class BaseColumns:
        
    def __new__( cls, *args, **kwargs ):
        
        # This class/subclasses should never be
        # instantiated.
        
        # help:
        # https://stackoverflow.com/questions/7989042/preventing-a-class-from-direct-instantiation-in-python
        #if issubclass( cls, StandardContextConventions ):
        raise SyntaxError( 'this is a static class and should never be instantiated' )
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# created
