# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Interface to the Neo4j server.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
# same project
from sparkling.neo4j.Connection import Connection as BaseConnection
from sparkling.grimoire.GrimoireNeo4jColumns import (
    Columns,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR
    )
from sparkling.grimoire.PlaylistColumns import ColumnsPlaylist, NEO4J_LABEL_PLAYLIST
# common
from sparkling.common import unique_loc

class Connection( BaseConnection ):
    
    # Custom connection to Neo4j server
    # made specifically for Grimoire.
    
    # override from parent
    Columns = Columns
    
    # static list
    _db_names = []
    
    def __init__( self, socket, username, password ):
        
        super( Connection, self ).__init__( socket, username, password )
        
    def dl_db_names( self ):
        
        # Always returns a list.
        
        # TODO
        # separate thread
        
        response = self.query( 'show databases;', db_name='system' )
        if response is None:
            log.error( 'failed to get neo4j db names, maybe the server went offline?' )
            self._db_names = []
            return self._db_names
        
        self._db_names = [ record['name'].strip() for record in response ]
        log.debug( 'successfully obtained %s db names'%len(self._db_names) )
        return self._db_names
    
    def import_from_csv( self, src, db_name ):
        
        # Imports rows from .csv into current playlist database as nodes.
        # Supports reserved columns.
        # This means that I expect all column names to be either
        # - database-friendly (english, no whitespaces, etc)
        # or
        # - reserved (please see sparkling.neo4j.Columns).
        
        df = pd.read_csv( src )
        df.reset_index( drop=True, inplace=True ) # remove old identities
        df.fillna( '', inplace=True ) # i want only str
        
        nodes = self.df2nodes( df )
        
        identities = []
        for node in nodes:
            
            response = self.query(
                f'CREATE {node} RETURN ID({NODE}) AS id',
                db_name=db_name
                )
            
            if response is None:
                log.error( f'failed to connect to server to create node {node} in db {db_name}' )
            else:
                for record in response:
                    identities.append( str( record['id'] ) ) # !!!
        
        return identities
    
    def export_db_to_df( self, db_name ):
        
        # Saves whole db nodes data to disk.
        
        query = f'MATCH ({NODE}) RETURN {NODE}'
            
        # get df
        
        response = self.query( query, db_name=db_name )
            
        if response is None:
            log.error( 'can\'t get a response' )
            return
                
        df = pd.DataFrame([ r[NODE] for r in response ])
        df.index = [ r[NODE].id for r in response ]
        df.fillna( '', inplace=True )
        
        self.fill_reserved_columns(
            df, db_name=db_name
            )
        
        return df
        
    def replace_nodes( self, df, db_name ):
        
        #--------------------+++
        # Definitions.
        
        # short name for convenience
        c = Columns
        
        def replace_labels():
            
            # Update reserved column `labels`.
            
            if not c.neo4j_labels in df.columns:
                # nothing to replace - labels were
                # not chaged
                return
                
            # get old ones
            old_labels = None
            if response is not None:
                old_labels = []
                for r in response: old_labels.extend( r['labels_list'] )
                if len( old_labels )>0:
                    old_labels = LABEL_SEPARATOR.join(old_labels)
            
            # get new ones
            new_labels = LABEL_SEPARATOR.join(
                row[c.neo4j_labels].split(MULTIVALUE_SEPARATOR) )
            
            # replace
            
            none_to_some = len(new_labels)>0 and not( type(old_labels) == str )
            some_to_none = type(old_labels) == str and len(new_labels)==0
            some_to_some = type(old_labels) == str and len(new_labels)>0
            
            query = None
            if none_to_some:
                query = f'MATCH ({NODE}) WHERE ID({NODE})={identity} SET {NODE}:{new_labels}'
            elif some_to_none:
                query = f'MATCH ({NODE}) WHERE ID({NODE})={identity} REMOVE {NODE}:{old_labels}'
            elif some_to_some:
                query = f'MATCH ({NODE}) WHERE ID({NODE})={identity} REMOVE {NODE}:{old_labels} SET {NODE}:{new_labels}'
            if query:
                self.query( query, db_name=db_name )
        
        #--------------------+++
        # Actual code.
        
        # Fully replaces nodes with values from df.
        # I expect df.index to contain ID(node).
        
        for identity, row in df.fillna('').iterrows():
            
            # replace parameters
            params = self.convert_parameters( dict(row) )
            query = f'MATCH ({NODE}) WHERE ID({NODE})={identity} SET {NODE}={params} RETURN labels({NODE}) AS labels_list'
            response = self.query( query, db_name=db_name )
            
            # replace reserved columns
            # order is important, because i chain return
            # values in order to reduce the number of server requests
            replace_labels()
            
#---------------------------------------------------------------------------+++
# end 2023.10.03
# allow to manage playlists from here
