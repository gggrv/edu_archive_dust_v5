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
from sparkling.common import ( readf, savef )
from sparkling.neo4j import NODE, DEFAULT_DB
        
PLAYLIST_VERSION = '2.0'

class Columns:
    
    SCREEN_NAME = 'screen_name'
    ORDER = 'order'
    DB_NAME = 'db_name'
    PLAYLIST_DATA = 'playlist_data'

def playlist_version_is_correct( value ):
    return value == PLAYLIST_VERSION

def save_playlist( src, screen_name, order, db_name, playlist_data ):
    
    # Context-unaware function that saves any playlist to disk.
    
    # TODO
    # do it safely
    
    # i have some identities,
    # need to convert them to str
    if type( playlist_data ) == list:
        # convert list of identities
        # into string with whitespaces
        playlist_data = ' '.join(playlist_data)
    
    # order is important
    data = [
        PLAYLIST_VERSION,
        screen_name,
        order,
        db_name,
        playlist_data
        ]
        
    # save to disk
    savef( src, '\n'.join(data) )
    
def read_playlist( src, read_metadata, read_data ):
    
    # Context-unaware function that reads any playlist from disk.
    
    CHECK_AT_LEAST_SO_MANY_ITEMS = 5
    n_lines_to_read = 4 if not read_data else 5
    
    #----------------------+++
    # Definitions.
    
    def parse_identities():
        
        # Parses playlist_data - wither it is a rule, or
        # a list of identitites.
        
        # i want to read actual data
        
        playlist_data = values[4].strip()
        
        if playlist_data == '':
            # no identities or rules were defined
            # treat it as an empty list of identities
            return []
            
        # attempt to break down whitespace-separated list
        identities = playlist_data.split(' ')
        
        # make sure at least some items are ok,
        # no need to check whole array
        R = min( len(identities), CHECK_AT_LEAST_SO_MANY_ITEMS )
        for identity in identities[ :R ]:
            if not identity.isdecimal():
                # this is not a list of identities, but a
                # string with rule
                return playlist_data
            
        # i end up here if
        # all identites are valid
        return identities
    
    #----------------------+++
    # Actual code.
    
    # TODO
    # do it safely
    
    if not os.path.isfile(src):
        raise FileNotFoundError( src )
        
    # obtain necessary lines
    values = readf( src, n_lines=n_lines_to_read, join_lines=False )
    
    # make sure playlist version is correct
    p_version = values[0].strip()
    if not playlist_version_is_correct( p_version ):
        msg = f'unsupported playlist version: {p_version}'
        log.error( msg )
        raise ValueError( msg )
        
    c = Columns
    data = {
        c.SCREEN_NAME: values[1].strip(),
        c.ORDER: values[2].strip(),
        c.DB_NAME: values[3].strip(),
        } if read_metadata else {}
        
    if read_data:  
        data[c.PLAYLIST_DATA] = parse_identities()
            
    return data

def to_df( conn, db_name, playlist_data ):
    
    # Converts nodes from any playlist into df.
    
    if len(playlist_data)==0:
        return
    
    # get query
    query = conn.standard_identities_query( playlist_data ) \
        if type(playlist_data)==list else \
        playlist_data
        
    # get df
    
    response = conn.query( query, db_name=db_name )
        
    if response is None:
        log.error( 'can\'t get a response' )
        return
            
    df = pd.DataFrame([ r[NODE] for r in response ])
    df.index = [ r[NODE].id for r in response ]
    df.fillna( '', inplace=True )
    
    conn.fill_reserved_columns( df, db_name=db_name )
    
    return df
    
class Playlist:
    
    Columns = Columns
    
    # how will i save it on disk
    __src = None
    __basename = None
    
    # how will i show it on screen
    __screen_name = None # str
    
    # how will i sort it
    __order = None
    
    # what items to show
    __playlist_data = None # list or str
    
    # from which database
    __db_name = None
        
    def __init__( self,
        src,
        screen_name=None,
        order=None,
        db_name=None,
        playlist_data=None
        ):
        
        # unchangeable
        self.__src = src
        self.__basename = os.path.basename( self.__src )
        
        # attempt to read metadata from disk
        success = self.__load( True, False )
        if success:
            return
        
        # no metadata on disk exist yet,
        # maybe i want to define custom one
        # or use default
        
        # can be changed
        # must be not none
        self.__screen_name = self.__basename if screen_name is None else screen_name
        self.__order='' if order is None else order
        self.__db_name=DEFAULT_DB if db_name is None else db_name
        # may be none
        self.__playlist_data=playlist_data
        
    def __eq__( self, other ):
        if other is None: return False
        return self.__basename==other.basename()
    
    def __repr__(self):
        return self.__basename
        
    def identities( self ):
        
        # Returns a list of identities.
        # For external use only.
        
        if self.__playlist_data is None:
            self.__load( False, True )
        
        if type(self.__playlist_data) == list:
            return self.__playlist_data

    def query( self ):
        
        # Returns automatic rule instead of identities.
        # For external use only.
        
        if self.__playlist_data is None:
            self.__load( False, True )
    
        if type(self.__playlist_data) == str:
            return self.__playlist_data
    
    def src( self ):
        return self.__src
    def basename( self ):
        return self.__basename
    def screen_name( self ):
        return self.__screen_name
    def order( self ):
        return self.__order
    def db_name( self ):
        return self.__db_name
            
    def __load( self, read_metadata, read_data ):
        
        # Attempts to read data from disk.
        # If none exists, that's ok!
        
        try:
            
            c = Columns
            
            data = read_playlist( self.__src, read_metadata, read_data )
            
            if c.SCREEN_NAME in data:
                self.__screen_name = data[c.SCREEN_NAME]
            if c.ORDER in data:
                self.__order = data[c.ORDER]
            if c.DB_NAME in data:
                self.__db_name = data[c.DB_NAME]
            if c.PLAYLIST_DATA in data:
                self.__playlist_data = data[c.PLAYLIST_DATA]
            
            return True
            
        except FileNotFoundError:
            
            # ah, so this palylist was defined, but not saved
            # to disk yet - it has no playlist_data;
            # i want to keep it's current metadata
            return False
        
        # failed for some other reason?
        return False
    
    def set_screen_name( self, screen_name ):
        # For external use only.
        self.__screen_name = screen_name
    
    def set_order( self, order ):
        # For external use only.
        self.__order = order
    
    def set_db_name( self, db_name ):
        # For external use only.
        self.__db_name = db_name
    
    def set_playlist_data( self, playlist_data, save=False ):
        # For external use only.
        self.__playlist_data = playlist_data
    
        if save:
            self.save()
            
    def add_playlist_data( self, additional_playlist_data, save=False ):
        
        # For external use only.
        
        data_was_not_loaded = self.__playlist_data is None
        
        if data_was_not_loaded:
            self.__load( False, True )
            
        # no data is available yet
        if self.__playlist_data is None:
            self.__playlist_data = additional_playlist_data
            return True
        
        # some data is available
        
        # either this is a rule-based playlist
        # or it is going to be
        # i don't want to change it like that -
        # i should replace the rule with
        # set_playlist_data() in such cases
        will_change_query = (
            type(self.__playlist_data)==str and
            not self.__playlist_data=='' ) \
            or type( additional_playlist_data )== str
        if will_change_query:
            
            # unload unneeded data
            if data_was_not_loaded:
                self.__playlist_data = None
            
            return False
            
        # add identities
        
        for identity in additional_playlist_data:
            if not identity in self.__playlist_data:
                # skip duplicates
                self.__playlist_data.append( identity )
        
        if save:
            self.save()
        
        # unload unneeded data
        if data_was_not_loaded:
            self.__playlist_data = None
            
        return True
                
    def open_playlist( self ):
        
        # Reads whole data.
        # For external use only.
        
        self.__load( False, True )
        
        if self.__playlist_data is None:
            self.__playlist_data = ''
    
    def is_open( self ):
        
        # For external use only.
        
        return not self.__playlist_data is None
    
    def close( self ):
        
        # For external use only.
        # Discards everything apart from metadata.
        
        self.__playlist_data = None
    
    def save( self ):
        
        # Attempts to save whole data to disk.
        # If only metadata was loaded, discards any additional
        # temporary stuff and keeps things as the were.
        
        data_was_not_loaded = self.__playlist_data is None
        
        if data_was_not_loaded:
            self.__load( False, True )
        
        # write whole playlist to disk
        save_playlist(
            self.__src,
            self.__screen_name,
            self.__order,
            self.__db_name,
            self.__playlist_data
            )
        
        # unload unneeded data
        if data_was_not_loaded:
            self.__playlist_data = None
        
    def df( self, conn ):
        
        # Returns dataframe with all nodes data.
    
        data_was_not_loaded = self.__playlist_data is None
        
        if data_was_not_loaded:
            self.__load( False, True )
            
        df = to_df(
            conn,
            self.__db_name,
            self.__playlist_data )
        
        # unload unneeded data
        if data_was_not_loaded:
            self.__playlist_data = None
            
        if df is None:
            return pd.DataFrame()
        
        return df
    
#---------------------------------------------------------------------------+++
# end 2023.05.12
# simplified
