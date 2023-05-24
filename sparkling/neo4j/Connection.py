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
    NODE, LABEL_SEPARATOR, Columns as c, DEFAULT_DB, MULTIVALUE_SEPARATOR
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
    
    if type(param_dict) is not dict: raise ValueError
    if len(param_dict)==0: return ''
    
    items = []
    for k,v in param_dict.items():
        
        if k==c._NEO4J_LABELS:
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

def _df2nodes( df, label=None ):
    
    nodes = []
    
    for _,row in df.iterrows():
        param_dict = {}
        for col in df.columns:
            if col==c._NEO4J_LABELS:
                label = row[col]
            else:
                #col = col.replace( ' ', '_' )
                param_dict[col] = row[col]
        node = _convert_node( NODE, label, param_dict )
        nodes.append(node)
        
    return nodes

class Connection:
    
    # This class allows to connect to a single
    # Neo4j server.
    
    # help:
    # https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7
    
    response2df = staticmethod( _response2df )
    convert_node = staticmethod( _convert_node )
    convert_parameters = staticmethod( _convert_parameters )
    convert_to_safe_string = staticmethod( _convert_to_safe_string )
    
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
        return not self.__driver is None
    
    def fill_reserved_columns( self, df, db_name=None ):
        
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
        df[c._NEO4J_LABELS] = texts
        
    def query( self, query, db_name=None ):
        
        # Allows to send any query to server.
        
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
# end 2023.05.25
# init configuration error checker
