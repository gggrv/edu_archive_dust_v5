# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
# same project
from sparkling.common.SomeDoer import SomeDoer as BaseSomeDoer
from sparkling.common import ( readf_yaml, readf, savef, unique_loc )
from sparkling.common.pyqt5.parentless.FileRenamerPresets import FileRenamerPresets
from sparkling.grimoire.GrimoireNeo4jConnection import (
    Connection,
    NODE, DB_DEFAULT
    )

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
# r'C:\custom_dir' + '\\' + row['custom_column1'] + '\\' + row['custom_column2'] + '\\' + os.path.basename(row[c.path])
# r'D:\custom_dir' + '\\' + row['custom_column5'] + '\\' + os.path.basename(row[c.path])
# r'E:\custom_dir' + '\\' + pd.to_datetime(row['timestamp']).strftime( r'%Y\%m\%Y%m%d_%H%M%S' ) + os.path.splitext(row[c.path])[1]
123:
  screen_name: basic neo4j
  labels: 
  db_name: neo4j
  rule: r'C:\custom_folder' + '\\' + os.path.splitext(row[c.path])[1]
  description: some basic rule
..."""
    
    savef( src, text )
        
def generate_trees( src ):
        
    # subject to change
    
    text = """---
#db:
#  rule name:
#    - command
null:
  labels:
- MATCH (n) return DISTINCT labels(n)
..."""
    
    savef( src, text )
        
class MainDoer( BaseSomeDoer ):
    
    # for external use
    PREFERRED_SAVE_DIR_NAME = 'grimoire'
        
    class Folders:
        
        PLAYLIST_LAYOUTS = 'playlist_layouts'
        PLAYLISTS = 'playlists'
        PLUGINS = 'plugins'
        EXPORTED_CSV = 'exported_csv'
        
    class Files:
    
        NEO4J_SETTINGS = 'neo4j_settings.yaml'
        TREES = 'trees.yaml'
        RENAMING_RULES = 'renaming_rules.yaml'
        PLAYLIST_PLUGINS = 'playlist_plugins.yaml'
        
    class Presets:
        
        FileRenamer = None
        
    conn = None # here will be a single connection
    
    def __init__( self,
        save_folder
        ):
        
        super( MainDoer, self ).__init__( save_folder )
        
        # paths
        self.Folders.PLAYLISTS = self.set_folder( self.Folders.PLAYLISTS )
        self.Folders.PLUGINS = self.set_folder( self.Folders.PLUGINS )
        self.Folders.EXPORTED_CSV = self.set_folder( self.Folders.EXPORTED_CSV )
        self.Folders.PLAYLIST_LAYOUTS = self.set_folder( self.Folders.PLAYLIST_LAYOUTS )
        self.Files.NEO4J_SETTINGS = self.set_file( self.Files.NEO4J_SETTINGS )
        self.Files.TREES = self.set_file( self.Files.TREES )
        self.Files.RENAMING_RULES = self.set_file( self.Files.RENAMING_RULES )
        self.Files.PLAYLIST_PLUGINS = self.set_file( self.Files.PLAYLIST_PLUGINS )
        # presets
        self.Presets.FileRenamer = FileRenamerPresets( self.Files.RENAMING_RULES )
    
    def __establish_connection( self ):
        
        # Connect to predefined neo4j server.
        # Return True/False depending on success.
        
        # TODO
        # do it safely
        
        if not self.conn is None:
            # i already have conn, not doing anything
            log.info( 'i already have conn, not doing anything' )
            return True
        
        src = self.Files.NEO4J_SETTINGS
        if not os.path.isfile( src ):
            # no connection settings exist yet,
            # prompt user, abort
            log.error( f'no connection settings exist yet, can\'t access server, please provide necessary data and restart the app: {src}' )
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
    
    def __generate_file_renaming_rules( self, src ):
        
        # Generates default preset for FileRenamer.
        
        if self.Presets.FileRenamer is None:
            return
        
        p = self.Presets.FileRenamer
        
        description = """some basic rule description
# example rules:
# r'C:\custom_dir' + '\\' + row['custom_column1'] + '\\' + row['custom_column2'] + '\\' + os.path.basename(row[c.path])
# r'D:\custom_dir' + '\\' + row['custom_column5'] + '\\' + os.path.basename(row[c.path])
# r'E:\custom_dir' + '\\' + pd.to_datetime(row['timestamp']).strftime( r'%Y\%m\%Y%m%d_%H%M%S' ) + os.path.splitext(row[c.path])[1]"""
        
        p.new_preset(
            unique_loc(),
            'Label1:Label2',
            'Example Renaming Preset',
            DB_DEFAULT,
            "r'C:\custom_folder' + '\\' + os.path.splitext(row[c.path])[1]",
            description
            )
            
    def autorun( self ):
        
        # attempt to connect to server
        success = self.__establish_connection()
        
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
# end 2023.07.25
# simplified
