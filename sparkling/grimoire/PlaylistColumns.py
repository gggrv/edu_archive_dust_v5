# -*- coding: utf-8 -*-
#Python utility "Playlist Columns". A static interface to specific nodes on a Neo4J server. Copyright (C) 2023 Anna Anikina
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------+++

# same project
# code
from sparkling.grimoire.GrimoireNeo4jColumns import (
    Columns,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR,
    SEARCH_INDEX_DEFAULT
    )
from sparkling.neo4j.Neo4jColumns import QUERY_KEYWORDS
# common
from sparkling.common import unique_loc
# enums
from sparkling.common.enums.Consent import EConsent

NEO4J_LABEL_PLAYLIST = 'DustGrimoirePlaylist'
NEO4J_LABEL_PLAYLIST_SELECTOR = 'DustGrimoirePlaylistSelector'

def _query_is_code( query ):
    
    # I may want to send
    # 1) actual database queries
    # 2) plaintext search.
    # In order to detect, what to do,
    # I look as uppercase/lowercase.
    
    # Uppercase = I want to send queries,
    # any other combination  = I want to perform plaintext search.
    
    # Very primitive, good enough for current task.
    
    for word in QUERY_KEYWORDS:
        if word in query:
            return True
        
    return False
    
class ColumnsPlaylist( Columns ):
    
    query_is_code = staticmethod( _query_is_code )
    
    # nodes from which database does this playlist hold?
    # i expect a single playlist to contain
    # nodes from a single db
    db_name = 'db_name'
    
    # which nodes were manually added to this playlist previously?
    identities = 'identities'
    
    # which nodes were automatically filtered in this playlist
    # previously?
    auto_query = 'auto_query'
    
    # which plugins were activated?
    plugins = 'plugins'
    
    forbid_deep_deletions = 'forbid_deep_deletions'
    
    # reserved optional `Columns` class keyword for
    # screen names
    texts = {
        db_name: 'DB name',
        identities: 'Node IDs',
        auto_query: 'Auto Query',
        plugins: 'Plugins',
        Columns.title: 'Playlist name',
        forbid_deep_deletions: 'Forbid deep deletions',
        }
    
    @classmethod
    def validate_auto_query( cls, playlist ):
        
        if not cls.auto_query in playlist:
            return
        
        query = playlist[cls.auto_query]
        if type(query)==str:
            if len( query.strip() ) > 0:
                # everything ok
                return
        
        # query is bad
        playlist.pop( cls.auto_query )
    
    @classmethod
    def validate_identities( cls, playlist ):
        
        if not cls.identities in playlist:
            return
        
        identities = playlist[cls.identities]
        if type(identities)==str:
            if len( identities.strip() ) > 0:
                # everything ok
                return
        
        # query is bad
        playlist.pop( cls.identities )
    
    @classmethod
    def validate_plugins( cls, settings ):
        
        if not cls.plugins in settings:
            return
        
        values = settings[cls.plugins]
        if type(values)==str:
            if len( values.strip() ) > 0:
                # everything ok
                return
        
        # bad
        settings.pop( cls.plugins )
    
    @classmethod
    def validate_deep_deletions( cls, playlist ):
        
        # make sure i have value
        if not cls.forbid_deep_deletions in playlist:
            # forbid by default
            playlist[cls.forbid_deep_deletions] = EConsent.CONSENT
            return
        
        value = playlist[cls.forbid_deep_deletions]
        if not ( value == EConsent.DECLINE ):
            # no idea which value it is, replace it
            # with consent
            playlist[cls.forbid_deep_deletions] = EConsent.CONSENT
            
    @classmethod
    def get_contents_query( cls, playlist ):
        
        # Creates appropriate `query` or `None`
        # for chosen `playlist definition` so that I can
        # download this playlist's contents easily
        # whenever suitable time comes.
        
        # it is technically possible that both
        # `identities` and `auto query` are present,
        # in such case i want to prioritize the `auto query`
        
        cls.validate_auto_query( playlist )
        if cls.auto_query in playlist:
            # i already have a database query
            return playlist[cls.auto_query]
        
        cls.validate_identities( playlist )
        if cls.identities in playlist:
            # i need to construct a standard identities
            # query with a predefined node variable name
            
            identities = playlist[cls.identities].split(' ')
            query = f'MATCH ({NODE}) ' \
                f'WHERE toString(ID({NODE})) IN {identities} ' \
                f'RETURN {NODE}'
                
            return query
        
        # no necessary fields = no query
    
    @classmethod
    def add_identities( cls, settings, identities ):
        
        # Standard way to add some identities
        # to current settings.
        
        if cls.identities in settings:
            new = settings[ cls.identities ].split(' ')
            new.extend(identities)
            settings[ cls.identities ] = ' '.join( set(new) )
        else:
            settings[ cls.identities ] = ' '.join( identities )
                
    @classmethod
    def get_plugin_changes( cls, old_settings, new_settings ):
        
        cls.validate_plugins( old_settings )
        cls.validate_plugins( new_settings )
        
        # make sure i have old plugins
        if not cls.plugins in old_settings:
            if cls.plugins in new_settings:
                return '', new_settings[cls.plugins]
            return '', ''
            
        # make sure i don't have new plugins
        if cls.plugins in new_settings:
            
            to_remove = []
            to_add = new_settings[cls.plugins].split( MULTIVALUE_SEPARATOR )
            for plugin_name in old_settings[cls.plugins].split( MULTIVALUE_SEPARATOR ):
                if plugin_name in to_add:
                    to_add.remove( plugin_name )
                elif not plugin_name in to_remove:
                    to_remove.append( plugin_name )
            return MULTIVALUE_SEPARATOR.join(to_remove), MULTIVALUE_SEPARATOR.join(to_add)
        
        # i want to remove all old and don't add any new
        return old_settings[cls.plugins], ''
            
    @classmethod    
    def new_playlist( cls, conn ):
        
        # For convenient use from GUI, code, anywhere.
        
        # `Playlists` are `nodes` in `default db`.
        # `Playlist` contains `nodes` from any single
        # chosen `db`.
        
        # Although I create only one playlist in this
        # function, I still use `df` rather then `dict`
        # because it allows me to store all necessaty
        # info in the perfect format.
        
        param_dict = {
            cls.title: unique_loc(),
            cls.db_name: DB_DEFAULT, # `nodes` from which `db` this playlist holds
            cls.forbid_deep_deletions: EConsent.CONSENT,
            }
        node = cls.convert_node( NODE, NEO4J_LABEL_PLAYLIST, param_dict=param_dict )
    
        # send this playlist definition specifically to default db
        response = conn.query( f'CREATE {node} RETURN {NODE}', db_name=DB_DEFAULT )
        df = cls.response2df( response, identity=True ) # i already have `identity` in `index`, but having it in column as well proved to be useful
        df[ cls.neo4j_labels ] = NEO4J_LABEL_PLAYLIST
                
        return df
            
    @classmethod    
    def _new_custom_playlist( cls, conn, settings ):
        
        # For manual use from code.
        # I assume that I know what I am doing and don't
        # need any additional verifications.
    
        node = cls.convert_node( NODE, NEO4J_LABEL_PLAYLIST, param_dict=settings )
    
        # send this playlist definition specifically to default db
        response = conn.query( f'CREATE {node} RETURN {NODE}', db_name=DB_DEFAULT )
        df = cls.response2df( response, identity=False ) # i already have `identity` in `index`
                
        return df
    
    @classmethod
    def _playlist_of_playlists( cls, conn ):
        
        # Makes sure that unique `playlist` that records ordering info
        # about other `playlists` exists.
        
        # This special `playlist` is expected to be
        # used only by `PalylistSelector`.
        
        # TODO
        # do all this safer
        
        # attempt to get existing
        node = cls.convert_node( NODE, NEO4J_LABEL_PLAYLIST_SELECTOR )
        response = conn.query( f'MATCH {node} RETURN {NODE}', db_name=DB_DEFAULT )
        
        if len(response) == 0:
            # need to create from scratch
        
            settings = {
                cls.db_name: DB_DEFAULT,
                cls.auto_query: f'MATCH ({NODE}:{NEO4J_LABEL_PLAYLIST}) RETURN {NODE} ORDER BY {NODE}.{cls.track_number}',
                }
            node = cls.convert_node( NODE, NEO4J_LABEL_PLAYLIST_SELECTOR, param_dict=settings )
            response = conn.query( f'CREATE {node} RETURN {NODE}', db_name=DB_DEFAULT )
        else:
            response = conn.query( f'MATCH {node} RETURN {NODE}', db_name=DB_DEFAULT )
        
        # download, parse into `settings`
        settings = response[0]['n']._properties
        settings[ cls.identity ] = response[0]['n'].id
        
        return settings
        
#---------------------------------------------------------------------------+++
# end 2023.10.21
# added NEO4J_LABEL_PLAYLIST_SELECTOR, _playlist_of_playlists
