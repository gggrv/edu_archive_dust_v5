# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtWidgets import (
    QTableView, QMessageBox, QComboBox, QTableWidgetItem
    )
# same project
from sparkling.common.pyqt5 import set_actions, remove_actions
from sparkling.grimoire.Playlist import Playlist
from sparkling.grimoire.pyqt5.PlaylistSelectorModel import PlaylistSelectorModel

class CustomCbx( QComboBox ):
    
    # Custom Combobox that emits not only current text,
    # but also a cell_rowiloc.
    
    TEXT_CHANGED = pyqtSignal( str, str )
    
    basename = None

    def __init__( self,
                  basename,
                  parent=None,
                  *args, **kwargs ):
        super( CustomCbx, self ).__init__( parent, *args, **kwargs )
        
        self.basename = basename
        self.currentTextChanged.connect( self.text_changed_event )
        
    def text_changed_event( self, text ):
        self.TEXT_CHANGED.emit( self.basename, text )
        
class PlaylistSelectorView( QTableView ):
    
    # Custom table view that works directly with
    # playlist manager.

    PLAYLIST_OPENED = pyqtSignal( Playlist )
    PLAYLIST_CLOSED = pyqtSignal( Playlist )
    #PLAYLIST_METADATA_CHANGED = pyqtSignal( dict )
    
    SEND_TO_CURRENT_ACTIVE_PLAYLIST = pyqtSignal( pd.DataFrame )
    
    IMPORT_CSV_TO_PLAYLIST = pyqtSignal( Playlist )
    EXPORT_PLAYLIST_TO_CSV = pyqtSignal( Playlist )
    EXPORT_DB_TO_CSV = pyqtSignal( str )
    
    __MODEL = None
    
    __conn = None

    def __init__( self,
                  playlist_manager,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistSelectorView, self ).__init__( parent=parent, *args, **kwargs )

        # immediately show data
        self.__MODEL = PlaylistSelectorModel( playlist_manager, parent=self )
        self.setModel( self.__MODEL )
        self.__create_cell_widgets()
        
        # appearance
        self.setShowGrid( False )
        self.setAlternatingRowColors( True )
        self.setSelectionBehavior( self.SelectRows )
        self.setWordWrap( False )
        self.setSortingEnabled( False )
        self.setContextMenuPolicy( Qt.ActionsContextMenu )

        # visible
        self.setColumnHidden( 0, True ) # basename
        self.setColumnHidden( 2, True ) # order
        self.sortByColumn( 2, Qt.AscendingOrder )
        
        self.__init_context_menu()
        
        # signals
        self.__MODEL.dataChanged.connect( self.__cell_text_changed_event )
        
    def __init_context_menu( self ):
        
        # Called once upon init.
        
        remove_actions( self )
        
        actions = [
            {
                'text': 'Open',
                'method': self.open_selected,
                },
            {
                'text': 'New',
                'method': self._cm_new_playlist,
                },
            {
                'text': 'Delete',
                'method': self.delete_selection,
                },
            {
                'text': 'Export db to .csv',
                'method': self._cm_export_db_to_csv,
                },
            {
                'text': 'Export playlist to .csv',
                'method': self._cm_export_playlist_to_csv,
                },
            {
                'text': 'Import .csv to db',
                'method': self._cm_import_csv_to_playlist,
                },
            ]
        
        set_actions( self, actions )
        
    def rowCount( self, parent=None ):
        return self.__MODEL.rowCount()

    def columnCount( self, parent=None ):
        return self.__MODEL.columnCount()
    
    def setCellWidget( self, row, column, w ):
        
        # help:
        # https://codebrowser.dev/qt5/qtbase/src/widgets/itemviews/qtablewidget.cpp.html#2355
        
        index = self.__MODEL.index( row, column )
        self.setIndexWidget( index, w )
        
    def __create_cell_widgets( self ):
        
        # Creates cell widgets for each playlist.
        # For internal use only.
        
        db_names = [] if self.__conn is None else self.__conn._db_names
        
        # for each playlist
        for rowiloc, p in enumerate( self.__MODEL.mgr._playlists ):
            
            # db selector
            cbx = CustomCbx( p.basename() )
            cbx.addItems( db_names )
            cbx.setCurrentText( p.db_name() )
            cbx.TEXT_CHANGED.connect( self.__cell_db_changed_event )
            self.setCellWidget( rowiloc, 3, cbx )
            
    def __cell_text_changed_event( self, index1, index2 ):
        
        # For internal use only.
        # Whenever text changes, I end up here.
        
        basename_coliloc = 0
        
        coliloc = index1.column()
        if coliloc==basename_coliloc:
            # don't allow to change basename
            return
        
        rowiloc = index1.row()
        new_value = self.__MODEL.data( self.__MODEL.index(rowiloc,coliloc) )
        basename = self.__MODEL.data( self.__MODEL.index(rowiloc,basename_coliloc) )
        k = self.__MODEL.column_keys[coliloc]
        
        new_data = {
            k: new_value
            }
        
        self.__MODEL.mgr.update_playlist( basename, new_data )
        
        #self.PLAYLIST_METADATA_CHANGED.emit( new_data )
            
    def __cell_db_changed_event( self, basename, db_name ):
        
        # For internal use only.
        # Whenever another db is selected via combobox, I end up here.
        
        c = Playlist.Columns
        
        new_data = {
            c.DB_NAME: db_name
            }
        
        self.__MODEL.mgr.update_playlist( basename, new_data )
        
        #self.PLAYLIST_METADATA_CHANGED.emit( new_data )
        
    def conn_changed_event( self, conn ):
        self.__conn = conn
        
        # reapply playlist manager
        self.switch_playlist_manager( self.__MODEL.mgr )
        
    def set_current_active_playlist( self, p ):
        self.__MODEL.mgr.set_current_active_playlist( p )
    def current_active_playlist( self ):
        return self.__MODEL.mgr.current_active_playlist()
    
    def selectedItems( self ):

        # help:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview

        sel = self.selectionModel()

        if not sel.hasSelection(): return []
        return sel.selectedRows()
      
    def selectedRowilocs( self ):

        rowilocs = []
        for item in self.selectedItems():
            rowiloc = item.row()
            rowilocs.append( rowiloc )
            
        return list( set(rowilocs) )
            
    def selectedPlaylists( self ):
        
        if self.__MODEL.rowCount()==0:
            return []
        
        rowilocs = self.selectedRowilocs()
        
        ps = [ self.__MODEL.mgr._playlists[rowiloc] for rowiloc in rowilocs ]
        return ps
    
    def select_next_row( self, rowiloc, after=True ):
        
        last_row = self.__MODEL.rowCount()-1
        next_row = 0 if after else 1
        if last_row>next_row:
            # selecting next row is possible
            if rowiloc>last_row:
                # current row is already last one
                self.selectRow( last_row if after else last_row-1 )
            else:
                self.selectRow( rowiloc )

        # its impossible to select next row
        # as it does not exist
        
    def delete_selection( self ):
        
        rowilocs = self.selectedRowilocs()
        if len(rowilocs)==0: return
        
        # make sure to close
        for iloc, p in enumerate( self.__MODEL.mgr._playlists ):
            if iloc in rowilocs and p.is_open():
                p.close()
                self.PLAYLIST_CLOSED.emit( p )
                
        # delete
        self.__MODEL.delete_playlists( rowilocs )

        self.select_next_row( rowilocs[0] )
        
    def get_open_playlists( self ):
        
        ps = []
        
        for p in self.__MODEL.mgr._playlists:
            if p.is_open():
                ps.append(p)
                
        return ps

    def switch_playlist_manager( self, playlist_manager ):
        
        # Completely changes current data.
        
        self.__MODEL.switch_playlist_manager( playlist_manager )
        self.__create_cell_widgets()
                
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
            
    def add_playlists( self, how_many ):
        
        # TODO
        # run __create_cell_widgets
        # only for necessary rows
        # rather the for each existing row
        
        self.__MODEL.add_playlists( how_many )
        self.__create_cell_widgets()
        
    def _cm_new_playlist( self ):
        self.add_playlists( 1 )
        
    def _cm_import_csv_to_playlist( self ):
        for p in self.selectedPlaylists():
            self.IMPORT_CSV_TO_PLAYLIST.emit( p )
        
    def _cm_export_db_to_csv( self ):
        for p in self.selectedPlaylists():
            self.EXPORT_DB_TO_CSV.emit( p.db_name() )
            
    def _cm_export_playlist_to_csv( self ):
        for p in self.selectedPlaylists():
            self.EXPORT_PLAYLIST_TO_CSV.emit( p )
        
    def open_selected( self ):
        
        # Opens specific playlists chosen from gui.
        
        ilocs = self.selectedRowilocs()
        if len(ilocs)==0: return
        
        for iloc, p in enumerate( self.__MODEL.mgr._playlists ):
            if iloc in ilocs:
                # open all that i want to open
                p.open_playlist()
                self.PLAYLIST_OPENED.emit( p )
            elif p.is_open():
                # close all others
                p.close()
                self.PLAYLIST_CLOSED.emit( p )
        
#---------------------------------------------------------------------------+++
# end 2023.05.12
# simplified
