# -*- coding: utf-8 -*-
#Python utility "Neo4J Columns". A static interface to specific nodes on a Neo4J server. Copyright (C) 2023 Anna Anikina
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------+++

from sparkling.neo4j.Neo4jColumns import (
    ColumnsNeo4j,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR,
    )

# name of predefined search indexes
# TODO
# move them to dedicated PresetsManager
SEARCH_INDEX_DEFAULT = 'defaultFields'

class Columns( ColumnsNeo4j ):
    
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
    
    # show/don't these columns in own gui
    columns_to_hide = 'columns_to_hide' # less priority
    columns_to_show = 'columns_to_show' # will override `columns_to_hide`
    
    @classmethod
    def is_move_protected( cls, row ):
        
        # Standard way to detect whether
        # this row is protected.
        
        # Absolutely any user value in the corresponding
        # field is treated as a protection consent.
        # For example value `False` is treated
        # as a `yes, protect me` string.
        
        if not cls.move_protected in row:
            return False
        
        if row[cls.move_protected] == '':
            return False
        
        return True
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# classmethod
