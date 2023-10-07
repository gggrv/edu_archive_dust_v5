# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Interface to the Neo4j server.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
from re import sub as resubstitute
# pip install
from neo4j import GraphDatabase
from neo4j.exceptions import ConfigurationError
import pandas as pd
# same project
from sparkling.neo4j.Columns import (
    Columns,
    # other packages may use items that are imported and unused
    # in this module
    # that's why i don't delete them
    NODE, LABEL_SEPARATOR, DB_DEFAULT, MULTIVALUE_SEPARATOR
    )

def _response2df( response, columns=None, identity=False, node_variable_name=None ):
    
    # Converts conn response to dataframe.
    
    if response is None:
        return
    if len( response )==0:
        return
    
    # short name
    n = node_variable_name
    if n is None:
        n = NODE
        
    # this response can be converted to df
    
    identities = [ r[n].id for r in response ]
    
    if columns==None:
        df = pd.DataFrame(
            [ r.data()[n] for r in response ],
            index=identities
            )
        if identity:
            df['identity'] = identities
        return df
    
    return pd.DataFrame([ dict(record) for record in response ])

def _convert_to_safe_string( some_string ):
    
    # Converts given python str into
    # an escaped string that can be safely sent in some neo4j query.
    
    safe_new = resubstitute( r'([\\\"\'])', r'\\\1', some_string )
    return f'\'{safe_new}\''

def _convert_parameters( param_dict ):
    
    # Converts python dictionary into a string with neo4j parameters.
    # Empty / invalid values are skipped.
    
    # help:
    # https://stackoverflow.com/questions/4202538/escape-special-characters-in-a-python-string
    
    # short name for convenience
    c = Columns
    
    if type(param_dict) is not dict: raise ValueError
    if len(param_dict)==0: return ''
    
    items = []
    for k,v in param_dict.items():
        
        if k==c.neo4j_labels:
            # skip reserved
            continue
        elif k==c.id:
            # skip reserved
            continue
        
        if not type(v)==str: v=str(v)
        if len(v)>0:
            v = resubstitute( r'([\\\"\'])', r'\\\1', v )
            items.append(  f'{k}:\'{v}\'' )
        
    if len(items)==0: return ''
    
    return '{%s}' % ', '.join(items)

def _convert_node( variable_name, label, param_dict=None ):
    
    # Converts python variables into a string with neo4j node.
    # Empty / invalid values are skipped.
    
    label = label if label else ''
    params = _convert_parameters( param_dict ) if param_dict else ''
    
    command = f"({variable_name} {params})" \
        if label=='' \
        else f"({variable_name}:{label} {params})"
        
    return command

def _convert_index_definition( index_name, fields ):
    
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
    
def _convert_index_search( index_name, query ):
    
    # Allows to send any `plaintext` query to server.
     
    query = _convert_to_safe_string( query )
        
    command =  f'CALL db.index.fulltext.queryNodes("{index_name}", {query}) YIELD node RETURN node as {NODE}'
    return command
    
def _df2nodes( df, label=None ):
    
    c = Columns
    nodes = []
    
    for _,row in df.iterrows():
        param_dict = {}
        for col in df.columns:
            if col==c.neo4j_labels:
                label = row[col]
            else:
                #col = col.replace( ' ', '_' )
                param_dict[col] = row[col]
        node = _convert_node( NODE, label, param_dict )
        nodes.append(node)
        
    return nodes

class InvalidConnectionError( Exception ):
    
    # help:
    # https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
    
    def __init__( self, message, errors ):
        super( InvalidConnectionError, self ).__init__( message )
            
        self.errors = errors
        
class Connection:
    
    # This class allows to connect to a single
    # Neo4j server.
    
    # help:
    # https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7
    
    # for ease of use in subclasses
    Columns = Columns
    
    response2df = staticmethod( _response2df )
    convert_node = staticmethod( _convert_node )
    convert_parameters = staticmethod( _convert_parameters )
    convert_to_safe_string = staticmethod( _convert_to_safe_string )
    convert_index_definition = staticmethod( _convert_index_definition )
    convert_index_search = staticmethod( _convert_index_search )
    
    df2nodes = staticmethod( _df2nodes )
    
    __driver = None
    
    def __init__( self, socket, username, password ):
        
        try:
            
            self.__driver = GraphDatabase.driver(
                socket,
                auth=( username, password ),
                )
            
        except ConfigurationError:
            
            return
    
    def close( self ):
        
        # Closes current connection.
        
        if self.__driver is not None:
            self.__driver.close()
            
    def is_valid( self ):
        
        # For external use only.
        
        return not self.__driver is None
    
    def fill_reserved_columns( self, df, db_name=None ):
        
        c = Columns
        
        # reserved columns
        
        identities = list( df.index.astype(str) )
        
        # reserved column for labels
        
        query = f'MATCH ({NODE}) ' \
            f'WHERE toString(ID({NODE})) IN {identities} ' \
            f'RETURN labels({NODE}) as labels_list'
        
        response = self.query( query, db_name=db_name )
        
        if response is None:
            msg = 'can\'t get a response'
            log.error( msg )
            raise ConnectionError( msg )
            
        texts = [ MULTIVALUE_SEPARATOR.join( r['labels_list'] ) for r in response ]
        df[c.neo4j_labels] = texts
        
    def query( self, query, db_name=None ):
        
        # Allows to send any `cipher` code query to server.
        
        if self.__driver is None:
            raise InvalidConnectionError
        
        session = None
        response = None
        
        try: 
            
            session = self.__driver.session(database=db_name) \
                if db_name is not None \
                else self.__driver.session()
                
            response = list( session.run(query) )
            
        except Exception as ex:
            
            log.error( f'query failed\n    query: {query}\n    db: {db_name}\n    because {ex}' )
            
        finally: 
            
            if session is not None:
                session.close()
                
        return response
    
#---------------------------------------------------------------------------+++
# end 2023.10.03
# added InvalidConnectionError
