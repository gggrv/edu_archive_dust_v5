# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Example custom main window.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QWidget, QFileDialog,
    QHBoxLayout, QSplitter, QTabWidget, QVBoxLayout,
    QDialog, QComboBox, QPushButton, QDialogButtonBox )
# same project
from sparkling.grimoire.GrimoireNeo4jConnection import Connection
# playlist selector
from sparkling.grimoire.pyqt5.PlaylistSelector import PlaylistSelector, ColumnsPlaylist
#from sparkling.grimoire.pyqt5.PlaylistPluginsPresetsEditor import PlaylistPluginsPresetsEditor
# playlist viewer
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer
from sparkling.grimoire.pyqt5.TabWidgetForPlaylistViewers import TabWidgetForPlaylistViewers
# filters
from sparkling.grimoire.pyqt5.DatabaseFilter import DatabaseFilter
#from sparkling.grimoire.pyqt5.TreeFilter import TreeFilter

class CentralWidget( QWidget ):
    
    CONNECTION_CHANGED = pyqtSignal( Connection )
    
    class Gui:
        
        tree_filter = None
        database_filter = None
        playlist_selector = None
        tab_widget = None
    
        side_tab_widget = None
        plugin_pane = None
    
        split_vleft = None
        split_hmid = None
    
    _own_doer = None

    def __init__( self,
                  own_doer,
                  parent=None,
                  *args, **kwargs ):
        super( CentralWidget, self ).__init__(
            parent=parent, *args, **kwargs )
        
        self._own_doer = own_doer
        
        # gui
        
        # help:
        # https://blog.csdn.net/huayunhualuo/article/details/102700647
        self.Gui.split_vleft = QSplitter( Qt.Vertical, parent=self )
        self.Gui.split_hmid = QSplitter( Qt.Horizontal, parent=self )
        
        self.Gui.split_vleft.setContentsMargins(0,0,0,0)
        self.Gui.split_hmid.setContentsMargins(0,0,0,0)
        
        self.Gui.playlist_selector = PlaylistSelector( parent=self )
        #self.Gui.tree_filter = TreeFilter( parent=self )
        self.Gui.database_filter = DatabaseFilter( parent=self )
        
        
        
        
        side_widget1 = QWidget( parent=self )
        side_lyt1 = QVBoxLayout()
        side_lyt1.addWidget( self.Gui.playlist_selector )
        #side_lyt1.addWidget( self.Gui.tree_filter )
        side_widget1.setLayout( side_lyt1 )
        
        side_widget2 = QWidget( parent=self )
        side_lyt2 = QVBoxLayout()
        side_lyt2.addWidget( self.Gui.database_filter )
        side_widget2.setLayout( side_lyt2 )
        
        #self.Gui.plugin_pane = PlaylistPluginsPresetsEditor(
        #    self._own_doer.Folders.PLUGINS,
        #    self._own_doer.Files.PLAYLIST_PLUGINS,
        #    parent=self )
        
        self.Gui.tab_widget = TabWidgetForPlaylistViewers( parent=self )
        
        self.Gui.side_tab_widget = QTabWidget( parent=self )
        self.Gui.side_tab_widget.setContentsMargins(0,0,0,0)
        self.Gui.side_tab_widget.addTab( side_widget1, '☰' )
        #self.Gui.side_tab_widget.addTab( self.Gui.plugin_pane, '⚙️' )
        self.Gui.side_tab_widget.addTab( side_widget2, '🔍' )

        # layouts
        
        lyt = QHBoxLayout()
        lyt.setContentsMargins( 0,0,0,0 )
        lyt.setSpacing(0)
        
        self.Gui.split_vleft.addWidget( self.Gui.side_tab_widget )
        self.Gui.split_hmid.addWidget( self.Gui.split_vleft )
        self.Gui.split_hmid.addWidget( self.Gui.tab_widget )
        
        # set default middle splitter position
        #self.Gui.split_hmid.setStretchFactor( 0,1 )
        self.Gui.split_hmid.setStretchFactor( 1,2 )
        
        lyt.addWidget( self.Gui.split_hmid )
        
        self.setLayout( lyt )
        
        # signals
        
        self.CONNECTION_CHANGED.connect( self.connection_changed_event )
        
        self.Gui.playlist_selector.PLAYLIST_OPEN.connect( self._playlist_open_event )
        self.Gui.playlist_selector.PLAYLIST_EDITED.connect( self._playlist_edited_event )
        self.Gui.tab_widget.tabCloseRequested.connect( self._playlist_close_event )
        
        self.Gui.database_filter.Gui.result_view.SEND_CONTENTS.connect( self._sent_contents_receive_event )
        
        # autorun
        
        # set all connections
        self.CONNECTION_CHANGED.emit( self._own_doer.conn )
        
        # populate playlist selector
        self.Gui.playlist_selector.download_playlists()
        
        # select and open first playlist
        #self.Gui.playlist_selector.selectRow( 0 )
        #self.Gui.playlist_selector.open_selected()
        
    def connection_changed_event( self, conn ):
        
        # I trigger this event myself.
        # Whenever needed, I may call `set_connection` on
        # child widgets manually - without using this `event`.
        
        # update all playlist selectors
        self.Gui.playlist_selector.set_connection( conn )
        self.Gui.database_filter.set_connection( conn )
        
        # update all playlist viewers
        tab_widget = self.Gui.tab_widget
        iloc = 0
        count = tab_widget.count()
        while iloc < count:
            w = tab_widget.widget(iloc)
            w.set_connection( conn )
        
    def _playlist_open_event( self, df ):
        
        # Whenever I want to open some playlists,
        # I do so by manipulating `playlist selector`.
        # I create a separate viewer for each playlist.
        # I don't close other currently open playlists.
        
        for loc, row in df.iterrows():
            
            settings = dict(row)
            settings[ColumnsPlaylist.identity] = loc
            
            # attempt to get existing dedicated viewer
            w = self.Gui.tab_widget.get_playlist_viewer( settings )
            if not w is None:
                # this playlist is already opened,
                # a viewer exists
                # no need to create another one
                continue
            
            # need to create dedicated viewer
            
            w = PlaylistViewer( parent=self,
                file_renamer_presets=self._own_doer.Presets.FileRenamer
                )
            
            w.set_connection( self._own_doer.conn )
            w.set_settings( settings )
            w.SEND_CONTENTS.connect( self._sent_contents_receive_event )
            w.OVERRIDE_SETTINGS.connect( self._request_playlist_settings_override_event )
            
            c = ColumnsPlaylist
            self.Gui.tab_widget.addTab( w, row[c.title] )
            
    def _playlist_edited_event( self, df ):
        
        # I edited some playlists through `PlaylistSelector`.
        # I want to update all relevant widgets.
        
        for loc, row in df.iterrows():
            
            settings = dict(row)
            settings[ColumnsPlaylist.identity] = loc
            
            # attempt to get existing dedicated viewer
            w = self.Gui.tab_widget.get_playlist_viewer( settings )
            if w is None:
                # this playlist is closed,
                # a viewer does not exist
                # no need to do anything
                continue
            
            # need to update dedicated viewer
            
            # TODO
            # at this moment i fully replace the contents
            # of the viewer. perhaps it would be better
            # to detect changes and act accordingly -
            # not every edit requires full widget
            # reinitialization
            
            w.set_settings( settings )
            
    def _playlist_close_event( self, tabiloc ):
        
        # Whenever I want to close some playlists,
        # I do so by manually closing tabs
        # in `tab widget for playlist viewers`.
        # I destroy a separate viewer for each playlist.
        
        # help:
        # https://stackoverflow.com/questions/61342380/pyqt5-closeable-tabs-in-qtabwidget
        
        w = self.Gui.tab_widget.widget( tabiloc )
        w.deleteLater()
        del w
        
        self.Gui.tab_widget.removeTab( tabiloc )
        
    def _sent_contents_receive_event( self, identities, settings ):
        
        # I end up here whenever I want to
        # send `df` somewhere.
        
        # most likely i want to add `identities` from `df.index`
        # into some existing playlist
        
        # any other functionality at this moment is not supported
        
        # do i have any playlists that can accept
        # `identities` with such `settings`?
        
        # short name for convenience
        c = ColumnsPlaylist
        
        # make sure i have all the necessary parties
        if self.Gui.playlist_selector is None:
            log.error( 'missing playlist_selector, can\'t accept' )
            return
        if not c.db_name in settings:
            log.error( 'missing `db_name`, can\'t accept' )
            return
        
        # get all compatible playlists names
        playlists = self.Gui.playlist_selector.get_df()
        mask = playlists[c.db_name] == settings[c.db_name]
        playlists = playlists[mask]
        
        # it is possible to send nodes back to self
        # it works, no problem
        # TODO
        # add code to prevent sending from self to self
        # this means that i need to include column `identity`
        # in playlist settings
        # because it makes no sense to detect
        # whether destination playlist = sender playlist
        # using any fields other then `identity`
        
        # make sure i have suitable destination playlists
        if len(playlists) == 0:
            log.error( 'no suitable destination playlists found, not doing anything' )
            return
            
        # ask confirmation
        # help:
        # https://www.pythonguis.com/tutorials/pyqt-dialogs/
        # https://stackoverflow.com/questions/5760622/pyqt4-create-a-custom-dialog-that-returns-parameters
        
        dlg = QDialog()
        dlg.setWindowTitle( 'Send where?' )
        
        dlg.cbx = QComboBox( parent=dlg )
        dlg.cbx.addItems( playlists[c.title] )
        
        dlg.button_box = QDialogButtonBox( parent=dlg )
        dlg.button_box.setStandardButtons(
            QDialogButtonBox.Ok
            |QDialogButtonBox.Cancel
            )
        dlg.button_box.accepted.connect( dlg.accept )
        dlg.button_box.rejected.connect( dlg.reject )
        
        lyt = QVBoxLayout()
        lyt.addWidget( dlg.cbx )
        lyt.addWidget( dlg.button_box )
        dlg.setLayout( lyt )
        
        if dlg.exec_():
            
            cbxiloc = dlg.cbx.currentIndex()
            
            # update the `settings`
            
            chosen_playlist = playlists.iloc[cbxiloc]
            identity = chosen_playlist.name
            settings = dict( chosen_playlist.dropna() )
            c.add_identities( settings, identities )
                
            # write it to db
            df = pd.DataFrame( [settings], index=[identity] )
            self.Gui.playlist_selector._accept_programmatic_edits( df )
            
    def _request_playlist_settings_override_event( self, settings ):
        
        # I end up here whenever
        # some `PlaylistViewer` has decided to change it's
        # own settings
        # and now wants `PlaylistSelector` to accept them.
        
        # make sure i have all the necessary parties
        if self.Gui.playlist_selector is None:
            log.error( 'missing playlist_selector, can\'t override' )
            return
            
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.identity in settings:
            log.debug( 'this playlist has no identity, no need to notify playlist selector' )
            return
        
        playlists = self.Gui.playlist_selector.get_df()
        if not settings[c.identity] in playlists.index:
            log.error( 'this playlist is not managed by current playlist selector, not doing anything' )
            return
        
        # write it to db
        df = pd.DataFrame( [settings], index=[ settings[c.identity] ] )
        self.Gui.playlist_selector._accept_programmatic_edits( df, tell_everyone=False )
        
    def _import_csv_to_playlist_event( self, p ):
        
        # Allows to select a .csv and import it to
        # any playlist.
    
        # help:
        # https://www.tutorialspoint.com/pyqt5/pyqt5_qfiledialog_widget.htm
    
        # ask for files
        dlg = QFileDialog()
        dlg.setFileMode( QFileDialog.AnyFile )
        if not dlg.exec_():
            return
            
        # got some
        fs = dlg.selectedFiles()
        for src in fs:
                
            # send the csv to db
            # TODO
            # validate/replace unsupported column names
            identities = self._own_doer.conn.import_from_csv(
                src, p.db_name()
                )
            
            # this playlist was closed
            # that means that no PlaylistViewer exists
            # i can do everything headlessly
            if not p.is_open():
                p.open_playlist()
                p.add_identities( identities, save=True )
                p.close()
                # nothing to do anymore
                return
            
            # this playlist was opened
            # that means that PlaylistViewer exists
            # i should update gui
            w = self.Gui.tab_widget.get_playlist_viewer( p )
            if w is None:
                # this playlist is open, but no PlaylistViewer exists???
                # that should not be possible, but i will
                # proceed as if everything is ok
                p.add_identities( identities, save=True )
                return
            w.add_identities( identities )
        
    def _export_db_to_csv_event( self, db_name ):
        self._own_doer.export_db_to_csv( db_name )
        
    def _export_playlist_to_csv_event( self, p ):
        self._own_doer.export_playlist_to_csv( p )
        
#---------------------------------------------------------------------------+++
# end 2023.05.25
# simplified
