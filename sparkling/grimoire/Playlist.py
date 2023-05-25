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

# by default empty playlists should contain no identities (list)
# rather the no rule (str)
DEFAULT_PLAYLIST_DATA = list

IDENTITIES_SEPARATOR = ' '

class Columns:
    
    BASENAME = 'basename'
    SCREEN_NAME = 'screen_name'
    ORDER = 'order'
    DB_NAME = 'db_name'
    PLAYLIST_DATA = 'playlist_data'
    
    texts = {
        BASENAME: 'Basename',
        SCREEN_NAME: 'Screen Name',
        ORDER: 'Sorting Order',
        DB_NAME: 'Database Name',
        PLAYLIST_DATA: 'Playlist Items'
        }

def save_playlist( src, screen_name, order, db_name,
    identities=None, autoquery=None ):
    
    # Context-unaware function that saves any playlist to disk.
    
    # TODO
    # do it safely
    
    # foolcheck
    has_identities = not identities is None
    has_autoquery = not autoquery is None
    if has_identities and has_autoquery:
        log.error( 'please make up your mind, a playlist can host only identities or only an autorule, not both' )
        return False
    if not has_identities and not has_autoquery:
        # no data, that's ok, save empty string
        autoquery = ''
    
    # get unified playlist_data
    playlist_data = IDENTITIES_SEPARATOR.join(identities) if has_identities else autoquery
    
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
    
    return True
    
def read_playlist( src, read_metadata, read_data ):
    
    # Context-unaware function that reads any playlist
    # raw data from disk.
    
    CHECK_AT_LEAST_SO_MANY_ITEMS = 5
    n_lines_to_read = 4 if not read_data else 5
    
    #----------------------+++
    # Definitions.
    
    def parse_identities():
        
        # Parses playlist_data - wither it is a rule, or
        # a list of identitites.
        # Returns either [...] or '...'
        
        # i want to read actual data
        
        playlist_data = values[4].strip()
        
        if playlist_data == '':
            # no identities or rules were defined
            # treat it as default
            return [] if DEFAULT_PLAYLIST_DATA==list else ''
            
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
            
        # i end up here if playlist_data is a list of identities
        # and all of them are valid
        return identities
    
    #----------------------+++
    # Actual code.
    
    # TODO
    # do it safely
    
    if not os.path.isfile(src):
        # no data on disk exists
        # silently ignore it
        # and pretend that data from disk is empty
        return {}
        
    # obtain necessary lines
    values = readf( src, n_lines=n_lines_to_read, join_lines=False )
    
    # make sure playlist version is correct
    p_version = values[0].strip()
    if not p_version==PLAYLIST_VERSION:
        msg = f'unsupported playlist version: {p_version}'
        log.error( msg )
        # treat this playlist as empty
        # possible data loss, so what? everything is in db
        return {}
        
    # construct playlist meta/data
    
    c = Columns
    data = {
        c.SCREEN_NAME: values[1].strip(),
        c.ORDER: values[2].strip(),
        c.DB_NAME: values[3].strip(),
        } if read_metadata else {}
        
    if read_data:
        data[c.PLAYLIST_DATA] = parse_identities()
        # at this moment
        # i am sure that i have valid not None playlist_data
            
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
        
        # attempt to read from disk
        # without opening
        success = self.__load( True, False )
        if success:
            # ok i read it,
            # but i may want to change something
            # on runtime
            # without saving
            new_data = {}
            if not screen_name is None:
                new_data[Columns.SCREEN_NAME] = screen_name
            if not order is None:
                new_data[Columns.ORDER] = order
            if not db_name is None:
                new_data[Columns.DB_NAME] = db_name
            if not playlist_data is None:
                new_data[Columns.PLAYLIST_DATA] = playlist_data
            self.set_data( new_data, save=False )
            
            # validate
            if self.__screen_name is None: self.__screen_name=self.__basename
            if self.__order is None: self.__order=''
            if self.__db_name is None: self.__db_name=DEFAULT_DB
            
            return
        
        # no metadata on disk exists yet,
        # maybe i want to define custom one
        # or use default
        
        # can be changed
        # must be not none
        self.__screen_name = self.__basename if screen_name is None else screen_name
        self.__order='' if order is None else order
        self.__db_name=DEFAULT_DB if db_name is None else db_name
        # may be none
        self.__playlist_data=playlist_data
        
        # if by this point __playlist_data is not None,
        # it means that this playlist is opened
        
    def __eq__( self, other ):
        
        # foolcheck
        if not type(other) is Playlist:
            return False
        
        return self.__basename==other.basename()
    
    def __repr__(self):
        
        status = 'closed' if self.__playlist_data is None else 'opened'
        text = f'{status} playlist {self.__basename}'
        
        return text
        
    def identities( self ):
        
        # Returns a list of identities.
        # For external use only.
        
        # make sure this playlist was explicitly opened
        was_closed = self.__playlist_data is None
        if was_closed:
            log.error( 'attempt to get identities from a closed playlist, please open it first' )
            return
        
        if type(self.__playlist_data) == list:
            # i can actually return identities
            return self.__playlist_data
        
        # this is some other-based playlist
        log.error( 'this playlist does not support identities' )

    def autoquery( self ):
        
        # Returns automatic rule instead of identities.
        # For external use only.
        
        # make sure this playlist was explicitly opened
        was_closed = self.__playlist_data is None
        if was_closed:
            log.error( 'attempt to get autoquery from a closed playlist, please open it first' )
            return
    
        if type(self.__playlist_data) == str:
            # i can actually return autorule
            return self.__playlist_data
    
        # this is some other-based playlist
        log.error( 'this playlist does not support autoquery' )
        
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
    
    def set_data( self, new_data, save=False ):
        
        # For external use only.
        
        c = Columns
        
        if c.BASENAME in new_data:
            self.__basename = new_data[c.BASENAME]
        if c.SCREEN_NAME in new_data:
            self.__screen_name = new_data[c.SCREEN_NAME]
        if c.ORDER in new_data:
            self.__order = new_data[c.ORDER]
        if c.DB_NAME in new_data:
            self.__db_name = new_data[c.DB_NAME]
            
        if c.PLAYLIST_DATA in new_data:
            self.__playlist_data = new_data[c.PLAYLIST_DATA]
    
        if save:
            self.save()
            
    def __load( self, read_metadata, read_data ):
        
        # Attempts to read data from disk.
        # If none exists, that's ok!
        
        # When `read_data`=True, I want to open this playlist
        # rather then simply load metadata.
        # So when read_data`=True, I make sure to
        # always set playlist_data
        # to some valid value.
        
        try:
            
            c = Columns
            
            data = read_playlist( self.__src, read_metadata, read_data )
            
            # metadata
            if c.SCREEN_NAME in data:
                self.__screen_name = data[c.SCREEN_NAME]
            if c.ORDER in data:
                self.__order = data[c.ORDER]
            if c.DB_NAME in data:
                self.__db_name = data[c.DB_NAME]
            
            if read_data:
                
                if c.PLAYLIST_DATA in data:
                    # i attempted to open this playlist
                    # i already know that i have a valid value
                    self.__playlist_data = data[c.PLAYLIST_DATA]
                    
                else:
                    # something happened when i was parsing this
                    # playlist
                    # make sure i have default valid value
                    self.__playlist_data = [] if DEFAULT_PLAYLIST_DATA is list else ''
            
            return True
            
        except FileNotFoundError:
            
            # ah, so this playlist was defined, but not saved
            # to disk yet - it has no playlist_data;
            # i want to keep it's current metadata
            # and treat it as an opened one
            
            if read_data:
                self.__playlist_data = [] if DEFAULT_PLAYLIST_DATA is list else ''
            
            return True
        
        # failed for some other reason?
        # most likely an exception will occur
        return False
                
    def open_playlist( self ):
        
        # Reads whole data.
        # For external use only.
        
        # attempt to read identities/rues form disk
        success = self.__load( False, True )
        
        # if i succeeded
        # at this moment i am 100% sure that playlist_data is valid
        return success
    
    def is_open( self ):
        
        # For external use only.
        
        is_closed = self.__playlist_data is None
        return not is_closed
    
    def close( self ):
        
        # For external use only.
        # Discards everything apart from metadata.
        
        self.__playlist_data = None
    
    def save( self ):
        
        # Attempts to save whole data to disk.
        
        was_closed = self.__playlist_data is None
        
        # make sure this playlist is open
        if was_closed:
            success = self.__load( False, True )
            if not success:
                log.error( 'this playlist was closed, something unpredictable happened when i tried to open it during saving - can\'t save' )
                return False
        
        # write whole playlist to disk
        save_playlist(
            self.__src,
            self.__screen_name,
            self.__order,
            self.__db_name,
            self.__playlist_data
            )
        
        # when needed close this playlist again
        if was_closed:
            self.__playlist_data = None
            
        return True
        
    def df( self, conn ):
        
        # Returns dataframe with all nodes data.
    
        was_closed = self.__playlist_data is None
        
        # make sure this playlist is open
        if was_closed:
            success = self.__load( False, True )
            if not success:
                log.error( 'this playlist was closed, something unpredictable happened when i tried to open it during getting df - can\'t proceed' )
                return
            
        df = to_df(
            conn,
            self.__db_name,
            self.__playlist_data )
        
        # when needed close this playlist again
        if was_closed:
            self.__playlist_data = None
            
        if df is None:
            return pd.DataFrame()
        
        return df
            
    def add_identities( self, identities, save=False ):
        
        # For external use only.
        
        # make sure this playlist was explicitly opened
        was_closed = self.__playlist_data is None
        if was_closed:
            log.error( 'can\'t add identities to a closed playlist, please open it first' )
            return
            
        # foolcheck
        
        is_rule_based = type(self.__playlist_data) is str
        if is_rule_based:
            log.error( 'can\'t add identities to a rule-based playlist' )
            return False
            
        is_identity_based = type(self.__playlist_data) is list
        if not is_identity_based:
            log.error( 'can\'t add identities to what the hell this playlist is' )
            return False
            
        # actually add the identities
        # skip duplicates
        for identity in identities:
            if not identity in self.__playlist_data:
                self.__playlist_data.append( identity )
        
        if save:
            self.save()
            
        return True
    
#---------------------------------------------------------------------------+++
# end 2023.05.25
# reduced ambiguities, simplified
# fixed custom data override loss on init
