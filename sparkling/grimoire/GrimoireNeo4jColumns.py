# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Reserved column names that have pre-existing functionality constraints.

from sparkling.neo4j.Columns import (
    Columns as BaseColumns,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR,
    )

class Columns( BaseColumns ):
    
    # I utilize `neo4j` nodes in a specific way.
    # I want to define some custom reserved columns (node field names)
    # that are valid only for this python
    # package.
    
    path = 'path' # full path to disk/net location, etc
    timestamp = 'timestamp' # usually YYYY.MM.DD HH:MM:SS
    
    # for comprehensive controlled ordering
    disk_number = 'disk_number'
    track_number = 'track_number'
    album = 'album'
    
    title = 'title' # user-friendly title
    desc = 'desc' # general description
    comment = 'comment' # own comment
    
    # don't rename/delete from disk
    move_protected = 'move_protected'
    
    @staticmethod
    def is_move_protected( row ):
        
        # Standard way to detect whether
        # this row is protected.
        
        # Absolutely any user value in the corresponding
        # field is treated as a protection consent.
        # For example value `False` is treated
        # as a `yes, protect me` string.
        
        c = Columns
        
        if not c._PROTECTED in row:
            return False
        
        if row[c._PROTECTED] == '':
            return False
        
        return True
    
#---------------------------------------------------------------------------+++
# end 2023.10.03
# created from another file
