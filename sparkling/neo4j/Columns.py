# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Reserved column names that have pre-existing functionality constraints.

NODE = 'n'
LABEL_SEPARATOR = ':'
DB_DEFAULT = 'neo4j'
MULTIVALUE_SEPARATOR = '; '

class Columns:
    
    # Reserved node field names.
    
    id = 'id' # ID(node)
    db_name = 'db_name' # which database does this node belong to
    
    neo4j_labels = 'neo4j Label' # can contain multiple ones
    
#---------------------------------------------------------------------------+++
# end 2023.10.06
# added `db_name`
