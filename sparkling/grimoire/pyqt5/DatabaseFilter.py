# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Allows to perform neo4j queries from GUI.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import pandas as pd
# pip install
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout,
    QLineEdit, QHBoxLayout, QLabel
    )
# same project
from sparkling.neo4j import NODE
from sparkling.common.pyqt5 import ( set_actions, remove_actions )
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer, Playlist
from sparkling.grimoire.PlaylistManager import DEFAULT_PLAYLIST_SCREEN_NAME

PLAYLIST_BASENAME = 'temp'
PLACEHOLDER_QUERY = f'MATCH ({NODE}) RETURN {NODE} LIMIT 50'

class DatabaseFilter( QWidget ):
    
    SEND_TO_CURRENT_ACTIVE_PLAYLIST = pyqtSignal( pd.DataFrame )
    
    class Gui:
        current_playlist_lab = None
        searchbar = None
        result_view = None
    
    __db_name = None
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( DatabaseFilter, self ).__init__(
            parent, *args, **kwargs )
        
        # layout
        
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0,0,0,0)
        
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        
        # controls
        
        self.Gui.current_playlist_lab = QLabel( DEFAULT_PLAYLIST_SCREEN_NAME, parent=self )
        self.Gui.searchbar = QLineEdit( parent=self )
        self.Gui.result_view = PlaylistViewer( parent=self )
        
        query = PLACEHOLDER_QUERY
        self.Gui.searchbar.setPlaceholderText( query )
        self.Gui.searchbar.setText( query )
        
        self.Gui.result_view.setAcceptDrops(False)
        self.Gui.result_view.can_host_current_active_playlist = False
        
        # assemble
        
        lyt.addWidget( self.Gui.current_playlist_lab )
        lyt.addLayout( hbox )
        lyt.addWidget( self.Gui.searchbar )
        lyt.addWidget( self.Gui.result_view )
        self.setLayout( lyt )
        
        self.__init_context_menu()
        
        # autorun
        
        self.Gui.searchbar.editingFinished.connect( self.__submit_search_event )
        
    def __init_context_menu( self ):
        
        # Call once upon init.
        
        remove_actions( self.Gui.result_view )
        actions = [
            {
                'text': 'Send to current playlist',
                'method': self.__send_selection_to_current_active_playlist,
                },
            #{
            #    'text': 'Open file',
            #    'method': self.Gui.result_view.open_file,
            #    },
            #{
            #    'text': 'Open file location',
            #    'method': self.Gui.result_view.open_folder,
            #    },
            #{
            #    'text': 'Delete from view',
            #    'method': self.Gui.result_view.delete_selection,
            #    },
            ]
        
        set_actions( self.Gui.result_view, actions )
        
    def conn_changed_event( self, conn ):
        self.Gui.result_view.conn_changed_event( conn )
        
    def set_current_active_playlist( self, p ):
        
        # change db name
        self.Gui.current_playlist_lab.setText( p.screen_name() )
        self.__db_name = p.db_name()
        
        if not self.isVisible():
            # no point to redownload data into hidden
            # widget
            return
        
        # redownload data
        old_p = self.Gui.result_view._playlist
        
        p = Playlist(
            src=PLAYLIST_BASENAME,
            db_name=self.__db_name,
            playlist_data=PLACEHOLDER_QUERY
            ) if old_p is None else \
            Playlist(
                src=old_p.src(),
                db_name=self.__db_name,
                playlist_data=old_p.autoquery()
                )
        
        self.Gui.result_view.switch_playlist( p )
        
    def __submit_search_event( self ):
        
        self.Gui.result_view.switch_playlist( None )
        
        query = self.Gui.searchbar.text().strip()
        if query=='':
            return
        
        p = Playlist( PLAYLIST_BASENAME, db_name=self.__db_name, playlist_data=query )
        self.Gui.result_view.switch_playlist( p )
        
    def __send_selection_to_current_active_playlist( self ):
        
        df = self.Gui.result_view.selectedSubdf()
        self.SEND_TO_CURRENT_ACTIVE_PLAYLIST.emit( df )
        
#---------------------------------------------------------------------------+++
# end 2023.05.25
# switched to autoquery
