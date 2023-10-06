# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Example custom main window.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QWidget, QFileDialog,
    QHBoxLayout, QSplitter, QTabWidget, QVBoxLayout )
# same project
from sparkling.grimoire.GrimoireNeo4jConnection import Connection
# playlist selector
from sparkling.grimoire.pyqt5.PlaylistSelector import PlaylistSelector, ColumnsPlaylist
#from sparkling.grimoire.pyqt5.PlaylistPluginsPresetsEditor import PlaylistPluginsPresetsEditor
# playlist viewer
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer
from sparkling.grimoire.pyqt5.TabWidgetForPlaylistViewers import TabWidgetForPlaylistViewers
# filters
#from sparkling.grimoire.pyqt5.DatabaseFilter import DatabaseFilter
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
        #self.Gui.database_filter = DatabaseFilter( parent=self )
        
        
        
        
        side_widget1 = QWidget( parent=self )
        side_lyt1 = QVBoxLayout()
        side_lyt1.addWidget( self.Gui.playlist_selector )
        #side_lyt1.addWidget( self.Gui.tree_filter )
        side_widget1.setLayout( side_lyt1 )
        
        side_widget2 = QWidget( parent=self )
        side_lyt2 = QVBoxLayout()
        #side_lyt2.addWidget( self.Gui.database_filter )
        side_widget2.setLayout( side_lyt2 )
        
        #self.Gui.plugin_pane = PlaylistPluginsPresetsEditor(
        #    self._own_doer.Folders.PLUGINS,
        #    self._own_doer.Files.PLAYLIST_PLUGINS,
        #    parent=self )
        
        self.Gui.tab_widget = TabWidgetForPlaylistViewers( parent=self )
        
        self.Gui.side_tab_widget = QTabWidget( parent=self )
        self.Gui.side_tab_widget.setContentsMargins(0,0,0,0)
        self.Gui.side_tab_widget.addTab( side_widget1, 'navi' )
        #self.Gui.side_tab_widget.addTab( self.Gui.plugin_pane, '⚙️' )
        self.Gui.side_tab_widget.addTab( side_widget2, 'filter' )

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
        self.Gui.tab_widget.tabCloseRequested.connect( self._playlist_close_event )
        
        #self.Gui.database_filter.SEND_TO_CURRENT_ACTIVE_PLAYLIST.connect( self.__send_to_current_active_playlist_event )
        #self.Gui.tree_filter.Gui.tree_view.SEND_TO_PLAYLIST.connect( self.__send_to_current_active_playlist_event )
        
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
            settings[ColumnsPlaylist.id] = loc
            
            # attempt to get existing dedicated viewer
            w = self.Gui.tab_widget.get_playlist_viewer( settings )
            if not w is None:
                # this playlist is already opened,
                # a viewer exists
                # no need to create another one
                return
            
            # need to create dedicated viewer
            
            w = PlaylistViewer( parent=self,
                file_renamer_presets=self._own_doer.Presets.FileRenamer
                )
            
            w.set_connection( self._own_doer.conn )
            w.set_settings( settings )
            
            c = ColumnsPlaylist
            self.Gui.tab_widget.addTab( w, row[c.title] )
            
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
