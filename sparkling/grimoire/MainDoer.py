# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.common.AutorunDoer import DAutorunDoer
from sparkling.common import ( readf_yaml, savef )
from sparkling.grimoire.GrimoireNeo4jConnection import (
    Connection,
    NODE, DB_DEFAULT
    )
from sparkling.grimoire.pyqt5.FileRenamer import PresetFileRenamer

def generate_neo4j_settings( src ):
        
    text = """---
# grimoire will not work in it's entirety without valid connection settings
socket: #bolt://localhost:7687
username: SOME_USERNAME
password: SOME_PASSWORD
..."""
        
    savef( src, text )
    
def generate_renaming_rules( src ):
        
    text = """---
# example rules:
# r'C:\custom_dir' + '\\\\' + row['custom_column1'] + '\\\\' + row['custom_column2'] + '\\\\' + os.path.basename(row['path'])
# r'D:\custom_dir' + '\\\\' + row['custom_column5'] + '\\\\' + os.path.basename(row['path'])
# r'E:\custom_dir' + '\\\\' + pd.to_datetime(row['timestamp']).strftime( r'%Y\%m\%Y%m%d_%H%M%S' ) + os.path.splitext(row['path'])[1]
123:
  screen_name: test renaming rule
  neo4j_labels: 
  db_name: neo4j
  rule: r'C:\custom_folder' + '\\\\' + os.path.splitext(row['path'])[1]
  description: some basic rule
..."""
    
    savef( src, text )
        
class MainDoer( DAutorunDoer ):
    
    # for external use
    PREFERRED_SAVE_DIR_NAME = 'grimoire'
        
    class Folders:
        PLUGINS = 'plugins'
        EXPORTED_CSV = 'exported_csv'
        
    class Files:
        NEO4J_SETTINGS = 'neo4j_settings.yaml'
        RENAMING_RULES = 'renaming_rules.yaml'
        
    class Presets:
        FileRenamer = None
        
    # here will be a single connection
    conn = None
    
    def __init__( self, save_folder ):
        
        super( MainDoer, self ).__init__( save_folder )
        
        # paths
        self.Folders.PLUGINS = self.set_folder( self.Folders.PLUGINS )
        self.Folders.EXPORTED_CSV = self.set_folder( self.Folders.EXPORTED_CSV )
        self.Files.NEO4J_SETTINGS = self.set_file( self.Files.NEO4J_SETTINGS )
        self.Files.RENAMING_RULES = self.set_file( self.Files.RENAMING_RULES )
        # presets
        if not os.path.isfile( self.Files.RENAMING_RULES ):
            generate_renaming_rules( self.Files.RENAMING_RULES )
        self.Presets.FileRenamer = PresetFileRenamer( self.Files.RENAMING_RULES )
    
    def _establish_connection( self ):
        
        # Connect to predefined neo4j server.
        # Return True/False depending on success.
        
        if not self.conn is None:
            log.info( 'i already have conn, not doing anything' )
            return True
        
        src = self.Files.NEO4J_SETTINGS
        if not os.path.isfile( src ):
            msg = f'no connection settings exist yet, can\'t access server, please provide necessary data and restart the app: {src}'
            log.error( msg )
            generate_neo4j_settings( src )
            os.startfile( src )
            return False
            
        settings = readf_yaml( src )
        
        conn = Connection(
            socket=settings['socket'],
            username=settings['username'],
            password=settings['password'],
            )
        
        if not conn.is_valid():
            log.error( 'this connection is not valid, not doing anything' )
            os.startfile( src )
            return False
        
        self.conn = conn
        return True
        
    def export_playlist_to_csv( self, p ):
        
        if not self.conn:
            log.error( 'no conn' )
            return
        
        df = p.df( self.conn )
        if len(df.index)==0:
            return
        
        # save to disk
        
        src = os.path.join(
            self.Folders.EXPORTED_CSV,
            f'partial_{p.db_name()}_from_{p.basename()}.csv'
            )
        
        df.to_csv( src, index=True ) # keep identities just in case
    
    def export_db_to_csv( self, db_name ):
        
        if not self.conn:
            log.error( 'no conn' )
            return
        
        df = self.conn.export_db_to_df( db_name )
        
        # save to disk
        
        src = os.path.join(
            self.Folders.EXPORTED_CSV,
            f'full_{db_name}.csv'
            )
        
        df.to_csv( src, index=True ) # keep identities just in case
            
    def autorun( self ):
        
        # attempt to connect to server
        success = self._establish_connection()
        
        if not success:
            msg = 'grimoire can\'t launch without connection to server, not doing anything'
            log.fatal( msg )
            return False, msg
        
        # i end up here only when i 100% have a valid
        # functional connection
        if len( self.conn._db_names )==0:
            self.conn.dl_db_names()
        
        # TODO
        # remember last used playist, auto load it
        
        return True, 'ok'
    
#---------------------------------------------------------------------------+++
# end 2023.10.19
# hardcoded field names in example renaming rules
