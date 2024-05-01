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

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
from re import sub as resubstitute
# pip install
import pandas as pd
# same project
from sparkling.common.BaseColumns import BaseColumns

NODE = 'n'
LABEL_SEPARATOR = ':'
DB_DEFAULT = 'neo4j'
MULTIVALUE_SEPARATOR = '; '

QUERY_KEYWORDS = [
    # help:
    # https://neo4j.com/docs/cypher-cheat-sheet/5/auradb-enterprise/
    'USE', 'CALL', 'YIELD'
    'MATCH', 'WHERE', 'OPTIONAL MATCH',
    'WITH',
    'RETURN',
    'ORDER BY', 'SKIP', 'LIMIT'
    ]
    
def _convert_to_safe_string( some_string ):
    
    # Converts given python str into
    # an escaped string that can be safely sent in some neo4j query.
    
    safe_new = resubstitute( r'([\\\"\'])', r'\\\1', some_string )
    return f'\'{safe_new}\''

class ColumnsNeo4j( BaseColumns ):
    
    # Reserved node field names.
    
    # ID(node)
    identity = 'identity'
    
    # which database does this node belong to
    db_name = 'db_name'
    
    # can contain multiple ones
    # i include whitespace, so that any attempts to write
    # this field to db fail
    neo4j_labels = 'neo4j Label'
    
    @classmethod
    def response2df( cls, response, columns=None, identity=False, node_variable_name=None ):
        
        # Converts conn response to dataframe.
        
        if response is None:
            return
        if len( response )==0:
            return
        
        # short name
        n = NODE if node_variable_name is None else node_variable_name
            
        # this response can be converted to df
        
        identities = [ r[n].id for r in response ]
        
        if columns==None:
            df = pd.DataFrame(
                [ r.data()[n] for r in response ],
                index=identities
                )
            if identity:
                df[cls.identity] = identities
            return df
        
        return pd.DataFrame([ dict(record) for record in response ])
    
    @classmethod
    def convert_node_parameters( cls, param_dict ):
        
        # Converts python dictionary into a string with neo4j parameters.
        # Empty / invalid values are skipped.
        
        # help:
        # https://stackoverflow.com/questions/4202538/escape-special-characters-in-a-python-string
        
        if type(param_dict) is not dict: raise ValueError
        if len(param_dict)==0: return ''
        
        items = []
        for k,v in param_dict.items():
            
            if k==cls.neo4j_labels:
                # skip reserved
                continue
            elif k==cls.identity:
                # skip reserved
                continue
            
            if not type(v)==str: v=str(v)
            if len(v)>0:
                v = resubstitute( r'([\\\"\'])', r'\\\1', v )
                items.append(  f'{k}:\'{v}\'' )
            
        if len(items)==0: return ''
        
        return '{%s}' % ', '.join(items)
    
    @classmethod
    def convert_node( cls, variable_name, label, param_dict=None ):
        
        # Converts python variables into a string with neo4j node.
        # Empty / invalid values are skipped.
        
        label = label if label else ''
        params = cls.convert_node_parameters( param_dict ) if param_dict else ''
        
        command = f"({variable_name} {params})" \
            if label=='' \
            else f"({variable_name}:{label} {params})"
            
        return command
    
    @classmethod
    def convert_index_definition( cls, index_name, fields ):
        
        # Creates default `full-text search index` on all `nodes`
        # in chosen `db`.
        
        # in order to do parse my db, i need to separately
        # set up `full-text search` on my `neo4j server`
        # help:
        # https://neo4j.com/docs/cypher-manual/current/indexes-for-full-text-search/
        
        formatted_fields = ', '.join([ 'n.' + field for field in fields ])
        
        # it will fail because apparently i need to specify labels
        # without labels = fail
        # so for now i'm not using this function and managing
        # db indexes manually
        command = f'CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS' \
            f' FOR (n)' \
            f' ON EACH [{formatted_fields}]'
            
        return command
        
    @classmethod
    def convert_index_search( cls, index_name, query, approximate=True ):
        
        # Allows to send any `plaintext` query to server.
        
        if approximate:
            
            # i don't need exact word matches - approximate is ok
            # help:
            # https://stackoverflow.com/questions/35105725/how-to-do-better-text-search-in-neo4j
            # https://neo4j.com/docs/cypher-manual/current/indexes-for-full-text-search/
            # http://lucenetutorial.com/lucene-query-builder.html
            
            # add special symbol to the end
            query += '~'
         
        query = _convert_to_safe_string( query )
            
        command =  f'CALL db.index.fulltext.queryNodes("{index_name}", {query}) YIELD node RETURN node as {NODE}'
        return command
        
    @classmethod
    def df2nodes( cls, df, label=None ):
        
        c = ColumnsNeo4j
        nodes = []
        
        for _,row in df.iterrows():
            param_dict = {}
            for col in df.columns:
                if col==c.neo4j_labels:
                    label = row[col]
                else:
                    #col = col.replace( ' ', '_' )
                    param_dict[col] = row[col]
            node = cls.convert_node( NODE, label, param_dict )
            nodes.append(node)
            
        return nodes
    
    @classmethod
    def fill_reserved_columns( cls, conn, df, db_name=None ):
        
        # reserved columns
        
        identities = list( df.index.astype(str) )
        
        # reserved column for labels
        
        query = f'MATCH ({NODE}) ' \
            f'WHERE toString(ID({NODE})) IN {identities} ' \
            f'RETURN labels({NODE}) as labels_list'
        
        response = conn.query( query, db_name=db_name )
        
        if response is None:
            msg = 'can\'t get a response'
            log.error( msg )
            raise ConnectionError( msg )
            
        texts = [ MULTIVALUE_SEPARATOR.join( r['labels_list'] ) for r in response ]
        df[cls.neo4j_labels] = texts
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# BaseColumns
