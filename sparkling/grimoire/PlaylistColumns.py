# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Reserved column names that have pre-existing functionality constraints.

# same project
# code
from sparkling.grimoire.GrimoireNeo4jColumns import (
    Columns,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR
    )
# common
from sparkling.common import unique_loc
# enums
from sparkling.common.enums.Consent import EConsent

NEO4J_LABEL_PLAYLIST = 'DustGrimoirePlaylist'

class ColumnsPlaylist( Columns ):
    
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
    
    @staticmethod
    def validate_auto_query( playlist ):
    
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.auto_query in playlist:
            return
        
        query = playlist[c.auto_query]
        if type(query)==str:
            if len( query.strip() ) > 0:
                # everything ok
                return
        
        # query is bad
        playlist.pop( c.auto_query )
    
    @staticmethod
    def validate_identities( playlist ):
    
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.identities in playlist:
            return
        
        identities = playlist[c.identities]
        if type(identities)==str:
            if len( identities.strip() ) > 0:
                # everything ok
                return
        elif type( identities )==list:
            if len( identities ) > 0:
                # everything ok
                return
        
        # query is bad
        playlist.pop( c.identities )
    
    @staticmethod
    def validate_deep_deletions( playlist ):
    
        # short name for convenience
        c = ColumnsPlaylist
        
        # make sure i have value
        if not c.forbid_deep_deletions in playlist:
            # forbid by default
            playlist[c.forbid_deep_deletions] = EConsent.CONSENT
            return
        
        value = playlist[c.forbid_deep_deletions]
        if not ( value == EConsent.DECLINE ):
            # no idea which value it is, replace it
            # with consent
            playlist[c.forbid_deep_deletions] = EConsent.CONSENT
            
    @staticmethod
    def get_contents_query( playlist ):
        
        # Creates appropriate `query` or `None`
        # for chosen `playlist definition` so that I can
        # download this playlist's contents easily
        # whenever suitable time comes.
        
        # short name for convenience
        c = ColumnsPlaylist
        
        # it is technically possible that both
        # `identities` and `auto query` are present,
        # in such case i want to prioritize the `auto query`
        
        c.validate_auto_query( playlist )
        if c.auto_query in playlist:
            # i already have a database query
            return playlist[c.auto_query]
        
        c.validate_identities( playlist )
        if c.identities in playlist:
            # i need to construct a standard identities
            # query with a predefined node variable name
            
            identities = playlist[c.identities]
            query = f'MATCH ({NODE}) ' \
                f'WHERE toString(ID({NODE})) IN {identities} ' \
                f'RETURN {NODE}'
                
            return query
        
        # no necessary fields = no query
    
    @staticmethod
    def get_playlists( conn ):
        
        # Download all info regarding playlists
        # from default db.
        
        query = f'MATCH ({NODE}:{NEO4J_LABEL_PLAYLIST}) RETURN {NODE}'
        response = conn.query( query, db_name=DB_DEFAULT )
        df = conn.response2df( response, identity=False ) # i already have `identity` in `index`
        
        return df
            
    @staticmethod    
    def new_playlist( conn ):
        
        # `Playlists` are `nodes` in `default db`.
        # `Playlist` contains `nodes` from any single
        # chosen `db`.
        
        # Although I create only one playlist in this
        # function, I still use `df` rather then `dict`
        # because it allows me to store all necessaty
        # info in the perfect format.
        
        # short name for convenience
        c = ColumnsPlaylist
        
        param_dict = {
            c.title: unique_loc(),
            c.db_name: DB_DEFAULT, # `nodes` from which `db` this playlist holds
            c.forbid_deep_deletions: '+',
            }
        node = conn.convert_node( NODE, NEO4J_LABEL_PLAYLIST, param_dict=param_dict )
    
        # send this playlist definition specifically to default db
        response = conn.query( f'CREATE {node} RETURN {NODE}', db_name=DB_DEFAULT )
        df = conn.response2df( response, identity=False ) # i already have `identity` in `index`
                
        return df
    
#---------------------------------------------------------------------------+++
# end 2023.10.06
# added `get_query`, others
