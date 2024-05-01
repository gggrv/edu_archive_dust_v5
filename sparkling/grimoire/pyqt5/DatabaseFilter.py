# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import pandas as pd
# pip install
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout,
    QLineEdit, QGridLayout, QLabel, QComboBox
    )
# same project
from sparkling.grimoire.PlaylistColumns import (
    ColumnsPlaylist,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR,
    SEARCH_INDEX_DEFAULT
    )
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer
# common
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions

QUERY_PLACEHOLDER = f'MATCH ({NODE}) RETURN {NODE} LIMIT 50'

class DatabaseFilter( QWidget ):
    
    # I can send queries to any db by manually changing
    # any playlist's `auto query` field in `PlaylistSelector`.
    # This widget allows me have a convenient text input field,
    # so that I don't need to navigate `Playlistselector`
    # and edit `nodes` every single time I want to search for
    # something.
    
    # I treat this widget like a complex container
    # for a custom special `PlaylistViewer`.
    
    # That custom special `PlaylistViewer` thinks
    # that is works with the `playlist` named `search`.
    # That `playlist` is virtual - I don't save it to `db`.
    # Every time I destroy this widget, this `playlist` is lost.
    
    _conn = None
    _virtual_settings = None
    
    class Gui:
        db_names = None
        searchbar = None
        result_view = None
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( DatabaseFilter, self ).__init__(
            parent, *args, **kwargs )
        
        # create my custom virtual `playlist` for searches
        # i perform searches by changing the `auto_query`
        # and `db_name`
        self._virtual_settings = {
            ColumnsPlaylist.title: 'search',
            ColumnsPlaylist.db_name: DB_DEFAULT,
            ColumnsPlaylist.auto_query: QUERY_PLACEHOLDER,
            }
        
        # layout
        
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0,0,0,0)
        
        hbox = QGridLayout()
        hbox.setContentsMargins(0,0,0,0)
        
        # search controls
        
        self.Gui.db_names = QComboBox( parent=self )
        self.Gui.db_names.addItem( DB_DEFAULT )
        self.Gui.db_names.currentTextChanged.connect( self._db_changed_event )
        
        self.Gui.searchbar = QLineEdit( parent=self )
        
        query = self._virtual_settings[ColumnsPlaylist.auto_query]
        self.Gui.searchbar.setPlaceholderText( query )
        self.Gui.searchbar.setText( query )
        
        hbox.addWidget( self.Gui.searchbar, 0, 0 )
        hbox.addWidget( self.Gui.db_names, 0, 3 )
        hbox.setColumnStretch( 0, 2 )
        
        # results view
        
        # TODO
        # enable row repositioning but still forbid
        # other drag/drops because useful;
        # not that important though
        self.Gui.result_view = PlaylistViewer(
            parent=self,
            selection_changed_event=False,
            accept_drops=False, # don't want to add data in db through it
            manually_reorder_rows=True
            )
        
        # assemble
        
        lyt.addLayout( hbox )
        lyt.addWidget( self.Gui.result_view )
        self.setLayout( lyt )
        
        self.__init_context_menu()
        
        # autorun
        
        self.Gui.searchbar.editingFinished.connect( self._submit_search_event )
        
    def __init_context_menu( self ):
        
        # Call once upon init.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        # it would be nice if i could perform
        # most of the playlist operations from this gui
        # widget as well (editing, deleting, etc) (except for adding)
        
        modifications = [
        {
            c.identity: 'grimoire/playlist_viewer/row/rename',
            c.enabled: False,
            c.visible: False,
            },
        {
            c.identity: 'grimoire/playlist_viewer/row/del_from_playlist',
            c.enabled: False,
            c.visible: False,
            },
        ]
        
        c.modify_actions( self.Gui.result_view, modifications )
        
    def set_connection( self, conn ):
        
        self._conn = conn
        
        self.Gui.result_view.set_connection( conn )
        
        db_names = []
        for db_name in self._conn._db_names:
            if not db_name == DB_DEFAULT:
                db_names.append( db_name )
        self.Gui.db_names.addItems( db_names )
        
        # populate widget with search results
        self.Gui.result_view.set_settings( self._virtual_settings )
        
    def _db_changed_event( self, db_name ):
        
        c = ColumnsPlaylist
        
        settings = self.Gui.result_view.settings()
        settings[ c.db_name ] = db_name
        
        # completely refresh the view
        self.Gui.result_view.set_settings( settings )
        
    def _submit_search_event( self ):
        
        # make sure i have some query
        query = self.Gui.searchbar.text().strip()
        query = query.strip()
        
        if query == '':
            query = QUERY_PLACEHOLDER
        
        # short name for convenience
        c = ColumnsPlaylist
        
        # detect my intention
        if not c.query_is_code(query):
            
            # instead of sending a direct query, i want to
            # parse plaintext fields without paying attention to
            # case registry
            
            # convert paintext into a valid db search index query
            query = ColumnsPlaylist.convert_index_search( SEARCH_INDEX_DEFAULT, query, approximate=True )
            
        # proceed as usual
        
        # it may happen that the default search index does
        # not exist yet on this db. in this case something will
        # silently fail, i need to manually monitor
        # such things and be aware of them
        # TODO
        # automatically manage search indexes
        # on db using custom PresetsManager
            
        # at this moment i can safely
        # send query to db
            
        # replace settings
        # to trigger download
        
        settings = self.Gui.result_view.settings()
        settings[ c.auto_query ] = query
        
        self.Gui.result_view.set_settings( settings )
        
#---------------------------------------------------------------------------+++
# end 2023.10.07
# simplified
