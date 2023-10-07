# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom table view.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
from PyQt5.QtCore import ( Qt, pyqtSignal )
from PyQt5.QtWidgets import ( QMessageBox )
# same project
# headless
from sparkling.grimoire.PlaylistColumns import ColumnsPlaylist
from sparkling.grimoire.GrimoireNeo4jColumns import Columns as ColumnsNeo4j, NODE
# gui
from sparkling.grimoire.pyqt5.NodeViewer import NodeViewer, ColumnsActionDefinitions
from sparkling.common.pyqt5.parentless.FileRenamer import FileRenamer
from sparkling.common.pyqt5 import ( mime2file, get_QItemSelection_rowilocs )
# common
from sparkling.common import ( unique_loc, delrem )

PLAYLIST_COLUMNS_TO_HIDE = [
    ColumnsPlaylist.identity,
    ColumnsPlaylist.db_name
    ]

def _open_path( df, dirname=False ):
    
    # Starts a file/folder with standard os methods.
    
    c = ColumnsNeo4j
    if not c.path in df.columns: return
    
    for src in df[c.path]:
        
        if type(src)==str:
            
            if os.path.exists(src):
                # this is a file on disk
                if dirname:
                    os.startfile( os.path.dirname(src) )
                else:
                    os.startfile( src )
            else:
                # maybe this is a link,
                # attempt to open it with standard means
                os.startfile( src )

def _delrem_df( df ):
    
    # Deletes paths in given df, returns
    # list of exceptions.
    
    # TODO
    # better and safer
    
    c = ColumnsNeo4j
    if not c.path in df.columns:
        return []
    
    exs = []
    
    for path in df[c.path]:
        if type(path)==str:
            try:
                delrem(path)
                exs.append(None)
            except Exception as ex:
                exs.append(ex)
                
    return exs

class PlaylistViewer( NodeViewer ):

    SEND_CONTENTS = pyqtSignal( list, dict )
    OVERRIDE_SETTINGS = pyqtSignal( dict )
    
    class Presets:
        
        FileRenamer = None # will be populated from outside
    
    def __init__( self,
                  file_renamer_presets=None,
                  selection_changed_event=True,
                  accept_drops=True,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistViewer, self ).__init__(
            parent=parent, *args, **kwargs )

        # presets
        if not file_renamer_presets is None:
            self.Presets.FileRenamer = file_renamer_presets
        
        # appearance
        self.setWordWrap( False )
        self.setAcceptDrops( accept_drops )
        self.setContextMenuPolicy( Qt.ActionsContextMenu )
        
        # interactions
        self.__init_context_menu()
        
        # signals
        
        if selection_changed_event:
            # i want to monitor how the user selects/deselects rows
            # help:
            # https://stackoverflow.com/questions/14803315/connecting-qtableview-selectionchanged-signal-produces-segfault-with-pyqt
            selectionModel = self.selectionModel()
            selectionModel.selectionChanged.connect( self.__selection_changed_event )
        
    def __init_context_menu( self ):
        
        # Called once during init.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        actions = [
             {
                 c.identity: 'grimoire/playlist_viewer/row/open_file',
                 c.text: 'Open',
                 c.method: self._cm_open_file,
                 c.shortcut: 'Alt+R',
                 },
             {
                 c.identity: 'grimoire/playlist_viewer/row/open_folder',
                 c.text: 'Open file location',
                 c.method: self._cm_open_folder,
                 c.shortcut: 'Alt+S',
                 },
             {
                 c.identity: 'grimoire/playlist_viewer/row/edit',
                 c.text: 'Edit',
                 c.method: self.launch_selection_editor,
                 c.shortcut: 'Alt+Return',
                 },
             {
                 c.identity: 'grimoire/playlist_viewer/row/rename',
                 c.text: 'Rename',
                 c.method: self.rename_selection,
                 c.shortcut: 'Alt+Left',
                 },
            {
                c.identity: 'grimoire/playlist_viewer/row/send_somewhere',
                c.text: 'Send...',
                c.method: self._cm_send_somewhere,
                },
            {
                c.identity: 'grimoire/playlist_viewer/row/del_from_playlist',
                c.text: 'Delete from playlist',
                c.method: self.del_from_view,
                c.shortcut: 'Del',
                },
            {
                c.identity: 'grimoire/playlist_viewer/row/del_from_db',
                c.text: 'Delete from database',
                c.method: self.del_from_view_db,
                c.shortcut: 'Alt+Shift+Down',
                },
            {
                c.identity: 'grimoire/playlist_viewer/row/del_from_disk',
                c.text: 'Delete from database and disk',
                c.method: self.del_from_view_db_disk,
                c.shortcut: 'Alt+Down',
                },
            ]
        
        c.remove_actions( self )
        c.add_actions( self, actions )
        
    def set_settings( self, settings ):
        
        # I want to fully replace current contents.
        
        # do what needs to be done
        super( PlaylistViewer, self ).set_settings( settings )
        
        # additinally i need to populate this viewer with
        # downloaded nodes
        
        # short name for convenience
        c = ColumnsPlaylist
        p = settings
        
        query = c.get_contents_query( p )
        if query is None:
            # this playlist is empty at this moment
            # and i can manually set auto query / add items
            # from search
            self.switch_df( pd.DataFrame(), columns_to_hide=PLAYLIST_COLUMNS_TO_HIDE )
            return
            
        response = self._conn.query( query, db_name=p[c.db_name] )
                
        df = pd.DataFrame([ r[NODE] for r in response ])
        df.index = [ r[NODE].id for r in response ]
        df.fillna( '', inplace=True )
        self._conn.fill_reserved_columns( df, db_name=p[c.db_name] )
        
        self.switch_df( df, columns_to_hide=PLAYLIST_COLUMNS_TO_HIDE )
        
    def mouseDoubleClickEvent( self, ev ):
    
        if ev.button()==Qt.LeftButton:
            self._cm_open_file()
        
    def focusInEvent( self, ev ):
        
        # When this widget was clicked, it's internal `playlist`
        # became global `current active playlist`.
        # Now this functionality is deprecated.
        # Will keep this for future ideas.
        
        # help:
        # https://stackoverflow.com/questions/28793440/pyqt5-focusin-out-events
        
        super( PlaylistViewer, self ).focusInEvent( ev )
        
    def launch_selection_editor( self ):
        
        super( PlaylistViewer, self ).launch_selection_editor()
        
    def _accept_selection_edits_event( self, changes ):
        
        super( PlaylistViewer, self )._accept_selection_edits_event( changes )
        
    def __selection_changed_event( self, selected, deselected  ):
        
        # Whenever I change current selection, I may want to
        # update the dependent widgets with new data.
        
        # help:
        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QItemSelectionModel.html#PySide2.QtCore.PySide2.QtCore.QItemSelectionModel.selectionChanged
        
        # foolcheck
        
        if selected.isEmpty() and deselected.isEmpty():
            # no changes, nothing to do
            log.debug( 'how did i end up here?' )
            return
        
        if len( self._parentless_windows )==0:
            # no dependent widgets, nothing to do
            return
        
        # get rowilocs
        selected_rowilocs = get_QItemSelection_rowilocs( selected )
        deselected_rowilocs = get_QItemSelection_rowilocs( deselected )
        
        # when i add selection, i need whole subdf
        new_subdf = self._MODEL.df.iloc[ selected_rowilocs ]
        
        # when i remove selection, i need only indexes
        rem_identities = list( self._MODEL.df.iloc[ deselected_rowilocs ].index )
        
        for w in self._parentless_windows:
            
            if type(w)==FileRenamer:
                w.change_contents( new_subdf, rem_identities )
        
    def dragEnterEvent( self, ev ):
        
        if self._playlist.autoquery():
            # this playlist is rule-based,
            # i don't want to edit it manually
            ev.ignore()
            return
        
        # this playlist is identities-based
        # i want to edit it manually
        ev.accept()
        
    def dragMoveEvent( self, ev ):
        
        if self._playlist.autoquery():
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
        
        if self._playlist.autoquery():
            msg = 'this playlist is rule-based, don\'t edit it manually!'
            log.error( msg )
            return
        
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
        
        c = ColumnsNeo4j
        
        identities = []
        for src in paths:
            
            # auto parse according to user preferences
            # TODO
            # plugin with custom parsing/renaming functions for different
            # paths, db_name and label
            # also make it available in path_eater
            param_dict = {
                c.path: src,
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
    
        if self._playlist.autoquery():
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
                
    
    def rename_selection( self ):
        
        c = ColumnsNeo4j
        
        if not c.path in self._MODEL.df.columns:
            return
        
        # obtain current selection
        df = self.selected_subdf()
    
        # launch renamer
        
        w = FileRenamer( presets_mgr=self.Presets.FileRenamer, parent=None )
        w.change_contents( df, None ) # populate with initial data
            
        w.EDITING_FINISHED.connect( self.__playlist_data_edited_event )
        
        self.__register_parentless_window(w)
        w.show()
        
    def forbid_deep_deletions( self, forbid ):
        
        # Most of the time I do not want
        # to delete items from db/disk.
        # In order to reduce the risk
        # of human error, allow toggling
        # respective context menus on/off.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        modifications = [
        {
            c.identity: 'grimoire/playlist_viewer/row/del_from_db',
            c.enabled: not forbid,
            c.visible: not forbid,
            },
        {
            c.identity: 'grimoire/playlist_viewer/row/del_from_disk',
            c.enabled: not forbid,
            c.visible: not forbid,
            },
        ]
        
        c.modify_actions( self, modifications )
    
    def del_from_view( self ):
        
        # I want to remove rows from current `view`
        # and update `playlist`.
        
        # TODO
        # allow this only if i have no `auto query` -
        # for example 
        # remove this option from context menu altogether
        # or manually switch playlit type in playlist selector
        # upon receiving signal
        
        super( PlaylistViewer, self ).del_from_view()
        
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.identity in self._settings:
            # i don't need to nofity playlist selector -
            # this playlist is not tracked
            return
        
        # i need to notify playlist selector
        
        self._settings[c.identities] = ' '.join(list( self._MODEL.df.index.astype(str) ))
        
        self.OVERRIDE_SETTINGS.emit( self._settings )
        
    def del_from_view_db( self ):
        
        # I want to delete rows from db and current view.
        
        if not self._conn.is_valid():
            msg = 'no valid _conn, not doing anything'
            log.critical( msg )
            return
        
        rowilocs = self.selected_rowilocs()
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
        
        subdf = self._MODEL.df.iloc[rowilocs]
        
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
        remaining_identities = list( self._MODEL.df.index.astype(str) )
        new_data = {Playlist.Columns.PLAYLIST_DATA:remaining_identities}
        self._playlist.set_data( new_data, save=True )
        
    def del_from_view_db_disk( self ):
        
        # I want to delete rows from disk, db and current view.
        
        if not self._conn.is_valid():
            msg = 'no valid _conn, not doing anything'
            log.critical( msg )
            return
        
        rowilocs = pd.Series( self.selected_rowilocs() )
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
        
        subdf = self._MODEL.df.iloc[rowilocs]
        
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
        remaining_identities = list( self._MODEL.df.index.astype(str) )
        new_data = {Playlist.Columns.PLAYLIST_DATA:remaining_identities}
        self._playlist.set_data( new_data, save=True )
    
    def _cm_open_file( self ):
        _open_path( self.selected_subdf(), dirname=False )
                
    def _cm_open_folder( self ):
        _open_path( self.selected_subdf(), dirname=True )
        
    def _cm_send_somewhere( self ):
        
        # I want to send selected nodes somewhere.
        # Don't know where yet.
        
        # Different widgets download different
        # node fields from db, so I should not send
        # the whole `df` - `identities` are enough to
        # enable the recipient redownload
        # all the necessary data.
        
        subdf = self.selected_subdf()
        if len( subdf.index ) > 0:
            identities = list( subdf.index.astype(str) )
            self.SEND_CONTENTS.emit( identities, self._settings )
        else:
            log.debug( 'no selection, nothing to send' )
            
#---------------------------------------------------------------------------+++
# end 2023.10.07
# added `_cm_send_somewhere`
