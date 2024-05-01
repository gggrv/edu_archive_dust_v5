# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from neo4j import GraphDatabase
from neo4j.exceptions import ConfigurationError
# same project
from sparkling.neo4j.Neo4jColumns import (
    ColumnsNeo4j,
    # other packages may use items that are imported and unused
    # in this module
    # that's why i don't delete them
    NODE, LABEL_SEPARATOR, DB_DEFAULT, MULTIVALUE_SEPARATOR
    )

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
    # can and should be overridden
    Columns = ColumnsNeo4j
    
    __driver = None
    
    def __init__( self, socket, username, password, custom_columns=None ):
        
        super( Connection, self ).__init__()
        
        # override columns
        if not custom_columns is None:
            self.Columns = custom_columns
        
        # initiate driver
        
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
# end 2023.10.14
# simplified
