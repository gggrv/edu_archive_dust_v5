# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal, Qt
# same project
# columns
from sparkling.grimoire.PlaylistColumns import (
    ColumnsPlaylist,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR,
    NEO4J_LABEL_PLAYLIST,
    NEO4J_LABEL_PLAYLIST_SELECTOR
    )
# common
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer
        
PLAYLIST_COLUMNS_TO_SHOW = [
    ColumnsPlaylist.title,
    ColumnsPlaylist.db_name,
    ]

class PlaylistSelector( PlaylistViewer ):
    
    # I want to browse existing playists.
    # Contents of opened playlists are available in a
    # dedicated `PlaylistViewer`.

    PLAYLIST_OPEN = pyqtSignal( pd.DataFrame )
    PLAYLIST_EDITED = pyqtSignal( pd.DataFrame )
    
    _conn = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistSelector, self ).__init__(
            parent=parent,
            selection_changed_event=False,
            accept_drops=False,
            manually_reorder_rows=True,
            *args, **kwargs )
        
        self.__init_context_menu()
        
        # this custom `playlist viewer` holds
        # very real `playlist` - it is saved to `db`
        
        # this `playlists` has custom `neo4j label` and i expect
        # that no other nodes with same label exist
        
        # this `playlists` records `identities` of other
        # `playlists
        
        # will not work w/o calling `set_connection`
        
    def set_connection( self, conn ):
        
        super( PlaylistSelector, self ).set_connection( conn )
        
        # upon executing `set_settings`, info regarding `playlists`
        # will be downloaded; actual contents of these `playlists`
        # will not be downloaded
        
        # TODO
        # for now i download full playlists metadata
        # and store it in self, but in the future
        # it might be possible that i don't need
        # all metadata
        
        settings = ColumnsPlaylist._playlist_of_playlists( self._conn )
        settings[ ColumnsPlaylist.columns_to_show ] = MULTIVALUE_SEPARATOR.join(PLAYLIST_COLUMNS_TO_SHOW)
        self.set_settings( settings )
        
    def __init_context_menu( self ):
        
        # Called once upon init.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        actions = [
            {
                c.identity: 'grimoire/playlist_selector/playlist/open',
                c.text: 'Open',
                c.method: self.open_selected_playlists,
                },
            {
                c.identity: 'grimoire/node_viewer/row/edit',
                c.text: 'Edit',
                c.method: self.launch_selection_editor,
                },
            {
                c.identity: 'grimoire/playlist_selector/playlist/new',
                c.text: 'New',
                c.method: self.new_playlist,
                },
            {
                c.identity: 'grimoire/playlist_selector/playlist/delete',
                c.text: 'Delete',
                c.method: self.del_from_view_db,
                },
            # {
            #     c.identity: 'grimoire/playlist_selector/playlist/export_db_to_csv',
            #     c.text: 'Export db to .csv',
            #     c.method: self.export_db_to_csv,
            #     },
            # {
            #     c.identity: 'grimoire/playlist_selector/playlist/export_playlist_to_csv',
            #     c.text: 'Export playlist to .csv',
            #     c.method: self.export_playlist_to_csv,
            #     },
            # {
            #     c.identity: 'grimoire/playlist_selector/playlist/import_csv_to_db',
            #     c.text: 'Import .csv to db',
            #     c.method: self.import_csv_to_playlist,
            #     },
            ]
        
        # i want to fully replace parent context menu
        # so that `PlaylistSelector`'s functionality is limited
        c.remove_actions( self )
        c.add_actions( self, actions )
        
    def the_dying_message( self ):
        
        # Whenever this widget/subclass is no longer needed,
        # I may want to remember certain things.
        
        c = ColumnsPlaylist
        
        # assign track numbers based on current ordering
        self._MODEL.df[c.track_number] = [ str(iloc+1) for iloc in range(self.rowCount()) ]
        
        # write to db
        self._accept_programmatic_edits( self._MODEL.df, tell_everyone=False )
        
    def mouseDoubleClickEvent( self, ev ):
    
        if ev.button()==Qt.LeftButton:
            self.open_selected_playlists()
        
    def new_playlist( self ):#, conn ):
        
        # Alternative `create new row`.
        
        c = ColumnsPlaylist
        
        df = c.new_playlist( self._conn )
        
        # i use df instead of `dict` in order to get
        # 100% accurate node.identity value
        # in current self._MODEL.df.index
        self.add_df( df )
        
    def open_selected_playlists( self ):
        
        # Opens specific playlists chosen from gui.
        
        rowilocs = self.selected_rowilocs()
        if len(rowilocs)==0: return
        
        df2open = self._MODEL.df.iloc[ rowilocs ]
        
        self.PLAYLIST_OPEN.emit( df2open )
    
    def launch_selection_editor( self ):
        
        # TODO
        # custom editor
        # with convenient comboboxes, etc
        
        constructor_parameters = {
            'master_column': ColumnsPlaylist.title,
            }
        
        # go directly to `NodeViewer`, skip `PlaylistViewer`
        super( PlaylistViewer, self ).launch_selection_editor( constructor_parameters=constructor_parameters )
        
    def _accept_programmatic_edits( self, df, tell_everyone=True ):
        
        # For careful manual use only.
        
        # I somehow programatically edited existing playlists
        # data.
        # I want to accept these changes.
        # It is important that I only edit existing -
        # do not delete/create anything.
        
        # Most likely I edited `auto query` or `identities`.
        
        # short name for convenience
        c = ColumnsPlaylist
        
        # i assume everything is clean and valid
        
        self._conn.replace_nodes( df, self._settings[c.db_name] )
        self.replace_subdf( df )
        self.reapply_columns_to_hide( columns_to_hide=PLAYLIST_COLUMNS_TO_SHOW, appropriate_reverse=True )
        
        # tell everyone to update
        if tell_everyone:
            self.PLAYLIST_EDITED.emit( df )
        
    def _accept_selection_edits_event( self, changes, db_name ):
    
        new_df = super( PlaylistViewer, self )._accept_selection_edits_event( changes, db_name )
        if new_df is None:
            # no change happened
            return
        
        self.reapply_columns_to_hide( columns_to_hide=PLAYLIST_COLUMNS_TO_SHOW, appropriate_reverse=True )
        
        # tell everyone that some playlists
        # changed somehow
        
        self.PLAYLIST_EDITED.emit( new_df )
        
#---------------------------------------------------------------------------+++
# end 2023.10.21
# wip save data to db
