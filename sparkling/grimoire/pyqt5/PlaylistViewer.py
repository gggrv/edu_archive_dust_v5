# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom table view.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
import shutil
# pip install
import pandas as pd
from PyQt5.QtCore import ( Qt, pyqtSignal )
from PyQt5.QtWidgets import ( QMessageBox )
# same project
from sparkling.neo4j.Columns import NODE, Columns as Neo4jColumns
from sparkling.common.pyqt5.PandasTableView import PandasTableView
from sparkling.grimoire.Playlist import Playlist
from sparkling.common.pyqt5.parentless.DfEditor import DfEditor
from sparkling.common.pyqt5.parentless.FileRenamer import FileRenamer
from sparkling.common.pyqt5 import ( set_actions, remove_actions, mime2file )
from sparkling.common import ( unique_loc, delrem )

def _open_path( df, dirname=False ):
    
    # Starts a file/folder with standard os methods.
    
    c = Neo4jColumns
    if not c.PATH in df.columns: return
    
    for src in df[c.PATH]:
        if type(src)==str:
            if os.path.exists(src):
                if dirname:
                    os.startfile( os.path.dirname(src) )
                else:
                    os.startfile( src )

def _delrem_df( df ):
    
    # Deletes paths in given df, returns
    # list of exceptions.
    
    # TODO
    # better and safer
    
    c = Neo4jColumns
    if not c.PATH in df.columns:
        return []
    
    exs = []
    
    for path in df[c.PATH]:
        if type(path)==str:
            try:
                delrem(path)
                exs.append(None)
            except Exception as ex:
                exs.append(ex)
                
    return exs

class PlaylistViewer( PandasTableView ):
    
    CURRENT_ACTIVE_PLAYLIST_CHANGED = pyqtSignal( Playlist )
    can_host_current_active_playlist = True

    # invisible spawned parentless windows will be saved here
    __parentless_windows = None # future list
    
    class Presets:
        
        FileRenamer = None # will be populated from outside
    
    _playlist = None
    _conn = None
    
    def __init__( self,
                  file_renamer_presets=None,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistViewer, self ).__init__(
            parent=parent, *args, **kwargs )

        # presets
        if not file_renamer_presets is None:
            self.Presets.FileRenamer = file_renamer_presets

        # dynamic
        self.__parentless_windows = []
        
        # appearance
        self.setWordWrap( False )
        self.setAcceptDrops(True)
        self.setContextMenuPolicy( Qt.ActionsContextMenu )
        
        # interactions
        self.__init_context_menu()
        
    def __init_context_menu( self ):
        
        # Called once during init.
        
        actions = [
             {
                 'text': 'Open',
                 'method': self._cm_open_file,
                 'shortcut': 'Alt+R',
                 },
             {
                 'text': 'Open file location',
                 'method': self._cm_open_folder,
                 'shortcut': 'Alt+S',
                 },
             {
                 'text': 'Edit',
                 'method': self.edit_selection,
                 'shortcut': 'Alt+Return',
                 },
             {
                 'text': 'Rename',
                 'method': self.rename_selection,
                 'shortcut': 'Alt+Left',
                 },
            {
                'text': 'Delete from playlist',
                'method': self.del_from_view,
                'shortcut': 'Del',
                },
            {
                'text': 'Delete from database',
                'method': self.del_from_view_db,
                'shortcut': 'Alt+Shift+Down',
                },
            {
                'text': 'Delete from database and disk',
                'method': self.del_from_view_db_disk,
                'shortcut': 'Alt+Down',
                },
            ]
        
        set_actions( self, actions )
        
    def switch_playlist( self, p ):
        
        # Completely replaces internal data.
        
        self._playlist = p
        
        if p is None:
            self.setEnabled( False )
            self.switch_df( pd.DataFrame() )
            return
        
        self.setEnabled( True )
        
        df = p.df( self._conn )
        self.switch_df( df )
        
    def add_df( self, df ):
        
        # Appends existing internal data with compatible df.
        # I know about this compatibility beforehand
        # and am 100% sure.
        
        identities = list( df.index.astype(str) )
        self._playlist.add_playlist_data( identities, save=True )
        
        super( PlaylistViewer, self ).add_df( df )
        
    def add_identities( self, identities ):
        
        # Appends existing internal data with some identities.
        
        # add to own playlist
        self._playlist.add_playlist_data( identities, save=True )
        
        #add to view
        query = self._conn.standard_identities_query( identities )
        temp_p = Playlist( 'temp', playlist_data=query )
        super( PlaylistViewer, self ).add_df( temp_p.df(self._conn) )
                
    def conn_changed_event( self, conn ):
        self._conn = conn
        
    def mouseDoubleClickEvent( self, ev ):
    
        if ev.button()==Qt.LeftButton:
            self._cm_open_file()
        
    def focusInEvent( self, ev ):
        
        # Whenever use clicks this widget, it's internal playlist
        # becomes global current active playlist.
        
        # help:
        # https://stackoverflow.com/questions/28793440/pyqt5-focusin-out-events
        
        super( PlaylistViewer, self ).focusInEvent( ev )
        
        if not self.can_host_current_active_playlist:
            return
        
        if self._playlist is None:
            return
        
        self.CURRENT_ACTIVE_PLAYLIST_CHANGED.emit( self._playlist )
        
    def __playlist_data_edited_event( self, changes ):
        
        # Happens whenever I change node values.
        # The playlist itself remains the same,
        # but data in the database should update.
        
        old_df, new_df = changes
        have_same_length = len(old_df.index) == len(new_df.index)
        have_some_rows = len(old_df.index)>0
        
        if not ( have_same_length and have_some_rows ):
            log.error( f'failed to apply changes after editing the df - content length mismatch: expected {len(old_df.index)}, got {len(new_df.index)}' )
            return
        if old_df.equals(new_df):
            log.info( 'the df was not edited - no changes detected, not doing anything' )
            return
            
        # change in database
        self._conn.replace_nodes( new_df, self._playlist.db_name() )
            
        # change in view
        self.replace_subdf( new_df )
        
        # no need to change in playlist because
        # shown identities did not change
        
    def dragEnterEvent( self, ev ):
        
        if not self._playlist.query() is None:
            # this playlist is rule-based,
            # i don't want to edit it manually
            ev.ignore()
            return
        
        # this playlist is identities-based
        # i want to edit it manually
        ev.accept()
        
    def dragMoveEvent( self, ev ):
        
        if not self._playlist.query() is None:
            # this playlist is rule-based,
            # i don't want to edit it manually
            ev.ignore()
            return
        
        # this playlist is identities-based
        # i want to edit it manually
        ev.accept()
        
    def _accept_custom_metadata( self, metadata ):
        
        # Accepts custom metadata that is not in db.
        # For external use only (plugins for example).
        
        identities = []
        
        if type(metadata)==pd.DataFrame:
            # df with some rows that are not in db
            raise NotImplementedError
        
        elif type(metadata)==dict:
            # one single row that is not in db
            # this is param_dict
            
            # parse reserved columns
            labels = ''
            if Neo4jColumns._NEO4J_LABELS in metadata:
                labels = metadata[Neo4jColumns._NEO4J_LABELS]
                del metadata[ Neo4jColumns._NEO4J_LABELS ]
            
            # send to db
            node = self._conn.convert_node( NODE, labels, param_dict=metadata )
            response = self._conn.query(
                f'CREATE {node} RETURN toString(ID({NODE})) AS identity',
                db_name=self._playlist.db_name()
                )
            
            if response is None:
                log.error( f'failed to connect to server to create node {node} in db {self._playlist.db_name()}' )
            else:
                for record in response:
                    identities.append( record['identity'] )
        
        elif type(metadata)==list:
            # list of dictionaries that are not in db
            
            for row in metadata:
                    
                # parse reserved columns
                labels = ''
                if Neo4jColumns._NEO4J_LABELS in row:
                    labels = row[Neo4jColumns._NEO4J_LABELS]
                    del row[ Neo4jColumns._NEO4J_LABELS ]
                    
                # send to db
                node = self._conn.convert_node( NODE, labels, param_dict=row )
                response = self._conn.query(
                    f'CREATE {node} RETURN toString(ID({NODE})) AS identity',
                    db_name=self._playlist.db_name()
                    )
            
                if response is None:
                    log.error( f'failed to connect to server to create node {node} in db {self._playlist.db_name()}' )
                else:
                    for record in response:
                        identities.append( record['identity'] )
        
        else:
            raise ValueError
            
        # send to internal data
        self.add_identities( identities )
        
    def __accept_dropped_paths( self, paths ):
        
        # I can call this method whenever I want my
        # playlist to accept new paths and save them to db.
        # For internal use only.
        
        c = Neo4jColumns
        
        identities = []
        for src in paths:
            
            # auto parse according to user preferences
            # TODO
            # plugin with custom parsing/renaming functions for different
            # paths, db_name and label
            # also make it available in path_eater
            param_dict = {
                c.PATH: src,
                c.TITLE: os.path.basename(src)
                }
            
            # send to db
            node = self._conn.convert_node( NODE, '', param_dict=param_dict )
            response = self._conn.query(
                f'CREATE {node} RETURN toString(ID({NODE})) AS identity',
                db_name=self._playlist.db_name()
                )
            
            if response is None:
                log.error( f'failed to connect to server to create node {node} in db {self._playlist.db_name()}' )
            else:
                for record in response:
                    identities.append( record['identity'] )
        
        # send to internal data
        self.add_identities( identities )

    def dropEvent( self, ev ):
    
        if not self._playlist.query() is None:
            # this playlist is rule-based,
            # i don't want to edit it manually
            ev.ignore()
            return
        
        # this playlist is identities-based
        # i want to edit it manually
        
        if ev.mimeData().hasUrls():
            # got some links
            
            is_some_url = r'://' in ev.mimeData().text()
            is_local_path = ev.mimeData().text().startswith( r'file://' )

            if is_local_path or is_some_url:
                # these links are ok
                
                paths = mime2file( ev.mimeData() ) \
                    if is_local_path \
                    else ev.mimeData().text().split('\n')
                    
                self.__accept_dropped_paths( paths )
                ev.accept()
                return
            
            else:
                # no idea what could be here
                # TODO
                ev.ignore()
                return
            
        # i got not links but something else
        log.error( 'unknown drops, not doing anything' )
        ev.ignore()

    def dragLeaveEvent( self, ev ):
        ev.accept()
                
    def edit_selection( self ):
        
        # Launches editor.
        
        c = Neo4jColumns
        
        subdf = self.selectedSubdf()
        if len(subdf.index)==0: return
        
        w = DfEditor(
            df=subdf,
            parent=None,
            display_vertical=False,
            )
        w.EDITING_FINISHED.connect( self.__playlist_data_edited_event )
        
        # attempt to set master column to path
        # may fail
        # TODO
        # external file with preferences
        # for each db and label
        w.set_master_column( c.PATH )
        
        self.__register_parentless_window(w)
        w.show()
    
    def rename_selection( self ):
        
        c = Neo4jColumns
        
        if not c.PATH in self.get_df_columns():
            return
        
        # obtain current selection
        df = self.selectedSubdf()
    
        # launch renamer
        
        w = FileRenamer(
            presets_mgr=self.Presets.FileRenamer,
            parent=None, df=df
            )
            
        w.EDITING_FINISHED.connect( self.__playlist_data_edited_event )
        
        self.__register_parentless_window(w)
        w.show()
    
    def del_from_view( self ):
        
        # I want to delete rows from current view.
        
        self.delete_selection()
        
        # del from playlist
        identities = list( self.get_df_index().astype(str) )
        self._playlist.set_playlist_data( identities, save=True )
    
    def del_from_view_db( self ):
        
        # I want to delete rows from db and current view.
        
        if not self._conn.is_valid():
            msg = 'no valid _conn, not doing anything'
            log.critical( msg )
            return
        
        rowilocs = self.selectedRowilocs()
        if len(rowilocs)==0: return
        
        # ask confirmation
        msg = QMessageBox()
        msg.setWindowTitle( 'Delete?' )
        msg.setStandardButtons(
            QMessageBox.Ok
            |QMessageBox.Cancel
            )
        msg.setDefaultButton(
            QMessageBox.Cancel
            )
        msg.setText( 'Selected rows will be \n- deleted from db\nAre you sure?' )
        retval = msg.exec_()
        if retval==QMessageBox.Cancel: return
        
        subdf = self.get_df().iloc[rowilocs]
        
        # del from db
        identities = list( subdf.index )
        query = f'MATCH ({NODE}) WHERE ID({NODE}) IN {identities} DETACH DELETE {NODE}'
        response = self._conn.query( query, db_name=self._playlist.db_name() )
        if response is None:
            log.error( 'failed to delete from server' )
            return
        
        # del from view
        self.delete_rows( rowilocs )
        self.select_next_row( rowilocs[0] )
        
        # del from playlist
        identities = list( self.get_df_index().astype(str) )
        self._playlist.set_playlist_data( identities, save=True )
        
    def del_from_view_db_disk( self ):
        
        # I want to delete rows from disk, db and current view.
        
        if not self._conn.is_valid():
            msg = 'no valid _conn, not doing anything'
            log.critical( msg )
            return
        
        rowilocs = pd.Series( self.selectedRowilocs() )
        if len(rowilocs)==0: return
        
        # ask confirmation
        msg = QMessageBox()
        msg.setWindowTitle( 'Delete twice?' )
        msg.setStandardButtons(
            QMessageBox.Ok
            |QMessageBox.Cancel
            )
        msg.setDefaultButton(
            QMessageBox.Cancel
            )
        msg.setText( 'Selected rows will be \n- deleted from db\n- deleted from disk\nAre you sure?' )
        retval = msg.exec_()
        if retval==QMessageBox.Cancel: return
        
        subdf = self.get_df().iloc[rowilocs]
        
        # del from disk
        exs = pd.Series( _delrem_df(subdf) )
        fail_rowilocs = exs[ exs.notna() ]
        subdf = subdf.iloc[ ~subdf.index.isin( fail_rowilocs.index ) ]
        rowilocs = rowilocs[ ~rowilocs.isin(fail_rowilocs.index) ]
        
        # del from db
        identities = list( subdf.index )
        query = f'MATCH ({NODE}) WHERE ID({NODE}) IN {identities} DETACH DELETE {NODE}'
        response = self._conn.query( query, db_name=self._playlist.db_name() )
        if response is None:
            log.error( 'failed to delete from server' )
            return
        
        # del from view
        self.delete_rows( rowilocs )
        self.select_next_row( rowilocs[0] )
        
        # del from playlist
        identities = list( self.get_df_index().astype(str) )
        self._playlist.set_playlist_data( identities, save=True )
    
    def _cm_open_file( self ):
        _open_path( self.selectedSubdf(), dirname=False )
                
    def _cm_open_folder( self ):
        _open_path( self.selectedSubdf(), dirname=True )
        
    def __register_parentless_window( self, w ):
        
        # I operate with many parentless windows.
        # They would disappear if no one referenced them.
        # Here I save those references.
    
        w.setObjectName(
            '%s%s'%( w.objectName(), unique_loc() )
            )
        w.OK_TO_CLOSE.connect( self.__remove_parentless_window_event )
        self.__parentless_windows.append(w)

    def __remove_parentless_window_event( self, object_name ):
        
        # I no longer need this parentless dialog.
        # I destroy the object and
        # remove reference to it from self.dialogs.

        for iloc, w in enumerate(self.__parentless_windows):
            
            if w.objectName()==object_name:

                self.__parentless_windows.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                # just die already
                return
            
#---------------------------------------------------------------------------+++
# end 2023.05.13
# fixed deleting from playlist
