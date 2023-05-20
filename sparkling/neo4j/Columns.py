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
    
    DESC = 'desc' # description
    
    PATH = 'path' # full path to disk/net location, etc
    
    TITLE = 'title' # beautiful title
    
    # reserved and invalid
    
    _NEO4J_LABELS = 'neo4j Label'
    
#---------------------------------------------------------------------------+++
# end 2022.08.03
# update
