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
from sparkling.grimoire.Connection import Connection, NODE, c, DEFAULT_DB
from sparkling.grimoire.PlaylistManager import PlaylistManager

def generate_neo4j_settings( src ):
        
    text = """---
socket: bolt://localhost:7687
username: <username>
password: <password>
..."""
        
    savef( src, text )
    
def generate_renaming_rules( src ):
        
    text = """---
# example rules:
# r'C:\custom_dir' + '\\' + row['custom_column1'] + '\\' + row['custom_column2'] + '\\' + os.path.basename(row[c.PATH])
# r'D:\custom_dir' + '\\' + row['custom_column5'] + '\\' + os.path.basename(row[c.PATH])
# r'E:\custom_dir' + '\\' + pd.to_datetime(row['timestamp']).strftime( r'%Y\%m\%Y%m%d_%H%M%S' ) + os.path.splitext(row[c.PATH])[1]
123:
  screen_name: basic neo4j
  labels: 
  db_name: neo4j
  rule: r'C:\custom_folder' + '\\' + os.path.splitext(row[c.PATH])[1]
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
        
        PLAYLISTS = 'playlists'
        PLUGINS = 'plugins'
        EXPORTED_CSV = 'exported_csv'
        
    class Files:
    
        NEO4J_SETTINGS = 'neo4j_settings.yaml'
        TREES = 'trees.yaml'
        RENAMING_RULES = 'renaming_rules.yaml'
        
    class Presets:
        
        FileRenamer = None
        
    conn = None # here will be a single connection
    playlist_manager = None
    
    # to be read from disk
    trees = None
    rules = None
    
    def __init__( self,
        save_folder
        ):
        
        super( MainDoer, self ).__init__( save_folder )
        
        # associate functions
        self._generate_file_functions = {
            MainDoer.Files.NEO4J_SETTINGS: generate_neo4j_settings,
            MainDoer.Files.TREES: generate_trees,
            MainDoer.Files.RENAMING_RULES: self.__generate_file_renaming_rules,
            }
        
        # set paths
        
        self.Folders.PLAYLISTS = self.set_folder( self.Folders.PLAYLISTS )
        self.Folders.PLUGINS = self.set_folder( self.Folders.PLUGINS )
        self.Folders.EXPORTED_CSV = self.set_folder( self.Folders.EXPORTED_CSV )
        
        self.Files.NEO4J_SETTINGS = self.set_file( self.Files.NEO4J_SETTINGS )
        self.Files.TREES = self.set_file( self.Files.TREES )
        self.Files.RENAMING_RULES = self.set_file( self.Files.RENAMING_RULES )
        
        self.Presets.FileRenamer = FileRenamerPresets( self.Files.RENAMING_RULES )
    
        # other
        
        self.playlist_manager = PlaylistManager( self.Folders.PLAYLISTS )
    
    def __establish_connection( self ):
        
        # Connect to predefined neo4j server.
        
        # TODO
        # do it safely
        
        if not self.conn is None:
            # i already have conn, not doing anything
            log.info( 'i already have conn, not doing anything' )
            return
        
        settings = readf_yaml( self.Files.NEO4J_SETTINGS )
        
        conn = Connection(
            socket=settings['socket'],
            username=settings['username'],
            password=settings['password'],
            )
        
        if not conn.is_valid():
            log.error( 'this connection is not valid, not doing anything' )
            return
        
        self.conn = conn
        
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
# r'C:\custom_dir' + '\\' + row['custom_column1'] + '\\' + row['custom_column2'] + '\\' + os.path.basename(row[c.PATH])
# r'D:\custom_dir' + '\\' + row['custom_column5'] + '\\' + os.path.basename(row[c.PATH])
# r'E:\custom_dir' + '\\' + pd.to_datetime(row['timestamp']).strftime( r'%Y\%m\%Y%m%d_%H%M%S' ) + os.path.splitext(row[c.PATH])[1]"""
        
        p.new_preset(
            unique_loc(),
            'Label1:Label2',
            'Example Renaming Preset',
            DEFAULT_DB,
            "r'C:\custom_folder' + '\\' + os.path.splitext(row[c.PATH])[1]",
            description
            )
            
    def autorun( self ):
        self.__establish_connection()
        
        if len( self.conn._db_names )==0:
            self.conn.dl_db_names()
        
        # TODO
        # remember last used playist, auto load it
    
#---------------------------------------------------------------------------+++
# end 2023.05.13
# simplified
