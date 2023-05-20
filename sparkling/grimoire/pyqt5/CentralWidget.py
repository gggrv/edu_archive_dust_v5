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
from sparkling.grimoire.Connection import Connection
from sparkling.grimoire.pyqt5.PlaylistSelectorView import PlaylistSelectorView
from sparkling.grimoire.pyqt5.DatabaseFilter import DatabaseFilter
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer
from sparkling.grimoire.pyqt5.PlaylistPluginsPresetsEditor import PlaylistPluginsPresetsEditor
#from sparkling.grimoire.pyqt5.TreeFilter import TreeFilter

class CentralWidget( QWidget ):
    
    CONN_CHANGED = pyqtSignal( Connection )
    
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
        
        self.Gui.playlist_selector = PlaylistSelectorView( self._own_doer.Doers.PlaylistManager, parent=self )
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
        
        self.Gui.plugin_pane = PlaylistPluginsPresetsEditor(
            self._own_doer.Folders.PLUGINS,
            self._own_doer.Files.PLAYLIST_PLUGINS,
            parent=self )
        
        
        
        
        self.Gui.tab_widget = QTabWidget( parent=self )
        self.Gui.tab_widget.setContentsMargins(0,0,0,0)
        
        self.Gui.side_tab_widget = QTabWidget( parent=self )
        self.Gui.side_tab_widget.setContentsMargins(0,0,0,0)
        self.Gui.side_tab_widget.addTab( side_widget1, 'navi' )
        self.Gui.side_tab_widget.addTab( self.Gui.plugin_pane, '⚙️' )
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
        
        self.CONN_CHANGED.connect( self.Gui.playlist_selector.conn_changed_event )
        self.CONN_CHANGED.connect( self.Gui.database_filter.conn_changed_event )
        #self.CONN_CHANGED.connect( self.Gui.tree_filter.conn_changed_event )
        
        self.Gui.playlist_selector.PLAYLIST_OPENED.connect( self.__playlist_opened_event )
        self.Gui.playlist_selector.PLAYLIST_CLOSED.connect( self.__playlist_closed_event )
        self.Gui.playlist_selector.IMPORT_CSV_TO_PLAYLIST.connect( self._import_csv_to_playlist_event )
        self.Gui.playlist_selector.EXPORT_PLAYLIST_TO_CSV.connect( self._export_playlist_to_csv_event )
        self.Gui.playlist_selector.EXPORT_DB_TO_CSV.connect( self._export_db_to_csv_event )
        
        self.Gui.database_filter.SEND_TO_CURRENT_ACTIVE_PLAYLIST.connect( self.__send_to_current_active_playlist_event )
        #self.Gui.tree_filter.Gui.tree_view.SEND_TO_PLAYLIST.connect( self.__send_to_current_active_playlist_event )
        
        #self.Gui.plugin_pane.REQUEST_PLUGIN_ENABLE.connect( self.REQUEST_PLUGIN_ENABLE.emit )
        #self.Gui.plugin_pane.REQUEST_PLUGIN_DISABLE.connect( self.REQUEST_PLUGIN_DISABLE.emit )
        
        # autorun
        
        self.CONN_CHANGED.emit( self._own_doer.conn )
        
        # select and open first playlist
        self.Gui.playlist_selector.selectRow( 0 )
        self.Gui.playlist_selector.open_selected()
        
    def __playlist_opened_event( self, p ):
        
        # For each opened playlist I create a separate viewer.
        
        for iloc in range( self.Gui.tab_widget.count() ):
            w = self.Gui.tab_widget.widget(iloc)
            if type(w)==PlaylistViewer:
                # this is correct class
                if w._playlist == p:
                    # this is correct playlist
                    # it is already opened,
                    # it already has dedicated viewer
                    # no need to create another one
                    return
        
        # need to create dedicated viewer
        
        w = PlaylistViewer( parent=self,
            file_renamer_presets=self._own_doer.Presets.FileRenamer
            )
        
        # signals
        
        self.CONN_CHANGED.connect( w.conn_changed_event )
        
        w.CURRENT_ACTIVE_PLAYLIST_CHANGED.connect( self.__current_active_playlist_changed_event )
        
        # populate
        w._conn = self._own_doer.conn
        w.switch_playlist( p )
        
        self.Gui.tab_widget.addTab( w, p.screen_name() )
        
    def __current_active_playlist_changed_event( self, p ):
        
        if p.basename()==self.Gui.playlist_selector.current_active_playlist().basename():
            # no change - i focused in the save playlist viewer
            return
        
        self.Gui.playlist_selector.set_current_active_playlist( p )
        self.Gui.database_filter.set_current_active_playlist( p )
        self.Gui.plugin_pane.set_current_active_playlist( p )
        
    def __playlist_closed_event( self, p ):
        
        # For each closed playlist I destroy separate viewer.
        
        iloc = 0
        while iloc<self.Gui.tab_widget.count():
            w = self.Gui.tab_widget.widget(iloc)
            if type(w)==PlaylistViewer:
                # this is correct class
                if w._playlist == p:
                    # this is correct playlist
                    # delete viewer
                    self.Gui.tab_widget.removeTab( iloc )
                    continue
            
            # this viewer does not need to be deleted,
            # advance to the next one
            iloc += 1
        
    def __send_to_current_active_playlist_event( self, df ):
        
        dest_p = self.Gui.playlist_selector.current_active_playlist()
        
        iloc = 0
        count = self.Gui.tab_widget.count()
        while iloc<count:
            w = self.Gui.tab_widget.widget(iloc)
            if type(w)==PlaylistViewer:
                # this is correct class
                if w._playlist.basename() == dest_p.basename():
                    # this is correct playlist
                    w.add_df( df )
                    # nothing to do anymore
                    return
                
            iloc += 1
        
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
            identities = self._own_doer.conn.import_from_csv(
                src, p.db_name()
                )
            
            # no view exists
            if not p.is_open():
                # add to playlist
                p.add_playlist_data( identities, save=True )
                # nothing to do anymore
                return
            
            # update corresponding view
            iloc = 0
            count = self.Gui.tab_widget.count()
            while iloc < count:
                w = self.Gui.tab_widget.widget(iloc)
                if type(w)==PlaylistViewer:
                    # this is correct class
                    if w._playlist.basename() == p.basename():
                        w.add_identities( identities )
                        # nothing to do anymore
                        return
                # wrong view, advane to next one
                iloc += 1
        
    def _export_db_to_csv_event( self, db_name ):
        self._own_doer.export_db_to_csv( db_name )
        
    def _export_playlist_to_csv_event( self, p ):
        self._own_doer.export_playlist_to_csv( p )
        
#---------------------------------------------------------------------------+++
# end 2023.05.17
# wip plugins
