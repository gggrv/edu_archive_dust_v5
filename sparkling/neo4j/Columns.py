# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Reserved column names that have pre-existing functionality constraints.

NODE = 'n'
LABEL_SEPARATOR = ':'
DEFAULT_DB = 'neo4j'
MULTIVALUE_SEPARATOR = '; '

class Columns:
    
    id = 'id' # ID(node)
    
    # custom
    
    comment = 'comment' # own comment
    
    desc = 'desc' # general description
    
    path = 'path' # full path to disk/net location, etc
    
    timestamp = 'timestamp'
    title = 'title' # user-friendly title
    
    # reserved and invalid
    
    _NEO4J_LABELS = 'neo4j Label'
    _PROTECTED = 'protected'
    
    @staticmethod
    def is_protected( dictionary ):
        
        # Standard way to detect whether
        # this row is protected.
        
        c = Columns
        
        if not c._PROTECTED in dictionary:
            return False
        
        if dictionary[c._PROTECTED] == '':
            return False
        
        return True
    
#---------------------------------------------------------------------------+++
# end 2023.10.02
# update
