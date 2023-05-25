# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project
from sparkling.grimoire.Playlist import Playlist, DEFAULT_DB
from sparkling.common.SomeDoer import SomeDoer
from sparkling.common import ( unique_loc )

DEFAULT_PLAYLIST_SCREEN_NAME = 'Default'
DEFAULT_PLAYLIST_BASENAME = '0'

class PlaylistManager( SomeDoer ):
    
    _playlists = None
    __current_active_playlist = None
    
    def __init__( self,
        save_folder
        ):
        
        super( PlaylistManager, self ).__init__( save_folder )
        
        self.__load()
        
        # always check/create default
        self.default_playlist()
        
    def __load( self ):
        
        # Attempts to read playlists metadata from disk.
        # If none exist, that's ok!
        
        # clear existing
        self._playlists = []
        
        # get all files in save dir,
        # treat them all like valid playlists
        root = self.get_save_folder()
        fs = os.listdir( root )
        
        for f in fs:
            src = os.path.join( root, f )
            p = Playlist( src )
            self._playlists.append( p )
            
    def current_active_playlist( self ):
        
        # at any point in time i have some active playlist -
        # maybe not a custom one, but the default
        if self.__current_active_playlist is None:
            return self.default_playlist()
        
        # ok, i have custom one
        return self.__current_active_playlist
    
    def set_current_active_playlist( self, current_active_playlist ):
        self.__current_active_playlist = current_active_playlist
            
    def get_playlist( self, basename ):
        
        # For external use only.
        
        for p in self._playlists:
            
            if p.basename()==basename:
                return p
        
    def playlists( self ):
        
        # For external use only.
        
        if self._playlists is None:
            self.__load()
        
        return self._playlists
        
    def new_playlist( self ):
        
        # Creates an empty playlist, does not write on disk yet.
            
        basename = unique_loc()
        
        src = os.path.join(
            self.get_save_folder(),
            basename
            )
    
        p = Playlist( src, screen_name=basename )
    
        self._playlists.append( p )
        return p
        
    def default_playlist( self ):
        
        # Returns THE unique Default playlist,
        # logically similar to foobar2000 Default -
        # always exists, always accepts data.
        # Does not write on disk yet.
        
        # it already exists
        for p in self._playlists:
            if p.basename() == DEFAULT_PLAYLIST_BASENAME:
                return p
            
        # it does not exist yet
    
        src = os.path.join(
            self.get_save_folder(), DEFAULT_PLAYLIST_BASENAME
            )
        
        p = Playlist( src,
            screen_name=DEFAULT_PLAYLIST_SCREEN_NAME,
            order='0',
            db_name=DEFAULT_DB,
            playlist_data=None )
        
        self._playlists.insert( 0, p )
        
        return p
        
    def delete_playlists( self, basenames ):
        
        default_was_deleted = False
        
        iloc = 0
        while iloc < len(self._playlists):
        
            p = self._playlists[iloc]
            basename = p.basename()
            if not basename in basenames:
                # don't delete this one
                iloc += 1
                continue
            
            # ready to delete
                
            src = p.src()
            if os.path.isfile( src ):
                os.remove( src )
                    
            self._playlists.pop( iloc )
            log.debug( f'ok deleting playlist {src}' )
            
            if basename==DEFAULT_PLAYLIST_BASENAME:
                default_was_deleted = True
            
        # recreate default one after deletion
        if default_was_deleted:
            self.default_playlist()
            
    def update_playlist( self, basename, new_data ):
        
        # Changes playlist metadata and data.
        # Saves on disk.
        # For external use only.
        
        for p in self._playlists:
            if not p.basename()==basename:
                continue
            
            p.set_data( new_data, save=True )
        
            # no need to do anything else
            return p
    
#---------------------------------------------------------------------------+++
# end 2023.05.25
# simplified
