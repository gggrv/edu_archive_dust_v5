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
from sparkling.grimoire.GrimoireNeo4jColumns import (
    Columns as ColumnsNeo4j,
    NODE, DB_DEFAULT
    )
# gui
from sparkling.grimoire.pyqt5.NodeViewer import NodeViewer, ColumnsActionDefinitions, _open_path, DfEditor
from sparkling.common.pyqt5 import ( get_QItemSelection_rowilocs )
# common
from sparkling.common import ( unique_loc )

PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR = [
    ColumnsPlaylist.identity,
    ColumnsPlaylist.db_name
    ]

class PlaylistViewer( NodeViewer ):

    SEND_CONTENTS = pyqtSignal( list, dict )
    OVERRIDE_SETTINGS = pyqtSignal( dict )
    
    # which tool to use to rename nodes
    _file_renamer_class = None
    
    def __init__( self,
                  selection_changed_event=True,
                  accept_drops=True,
                  node_editor_class=DfEditor,
                  file_renamer_class=None,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistViewer, self ).__init__(
            node_editor_class=node_editor_class,
            accept_drops=accept_drops,
            parent=parent, *args, **kwargs )
        
        # remember
        self._file_renamer_class = file_renamer_class
        
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
                c.identity: 'grimoire/playlist_viewer/row/send_somewhere',
                c.text: 'Send...',
                c.method: self._cm_send_somewhere,
                },
            {
                c.identity: 'grimoire/playlist_viewer/row/del_from_playlist',
                c.text: 'Remove from playlist',
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
            self.switch_df( pd.DataFrame(), columns_to_hide=PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR )
            return
            
        response = self._conn.query( query, db_name=p[c.db_name] )
        
        if response is None:
            # TODO
            # pop-up with log messages
            log.error( 'query most likely failed, please review db settings manually' )
            return
                
        df = pd.DataFrame([ r[NODE] for r in response ])
        df.index = [ r[NODE].id for r in response ]
        df.fillna( '', inplace=True )
        self._conn.fill_reserved_columns( df, db_name=p[c.db_name] )
        
        self.switch_df( df, columns_to_hide=PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR )
        
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
        
    def _accept_selection_edits_event( self, changes, db_name ):
        
        super( PlaylistViewer, self )._accept_selection_edits_event( changes, db_name )
        
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
            
            if type(w)==self._file_renamer_class:
                c = ColumnsPlaylist
                db_name = self._settings[c.db_name] if c.db_name in self._settings else DB_DEFAULT
                w.change_items( new_subdf, rem_identities, db_name )
        
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
        
        super( PlaylistViewer, self ).del_from_view_db()
    
        c = ColumnsPlaylist
        if not c.identity in self._settings:
            # i don't need to nofity playlist selector -
            # this playlist is not tracked (is not a `node` in `db` -
            # just a random `dict`)
            return
        
        # i need to notify playlist selector
        self._settings[c.identities] = ' '.join(list( self._MODEL.df.index.astype(str) ))
        self.OVERRIDE_SETTINGS.emit( self._settings )
        
    def del_from_view_db_disk( self ):
        
        # I want to delete rows from disk, db and current view.
        
        super( PlaylistViewer, self ).del_from_view_db_disk()
    
        c = ColumnsPlaylist
        if not c.identity in self._settings:
            # i don't need to nofity playlist selector -
            # this playlist is not tracked
            return
        
        # i need to notify playlist selector
        self._settings[c.identities] = ' '.join(list( self._MODEL.df.index.astype(str) ))
        self.OVERRIDE_SETTINGS.emit( self._settings )
    
    def _add_to_view_db( self, items, already_parsed,
        parsing_function=None ):
        
        super( PlaylistViewer, self )._add_to_view_db( items, already_parsed, parsing_function=parsing_function )
        
        self.OVERRIDE_SETTINGS.emit( self._settings )
        
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
        # enable the recipient to redownload
        # all the necessary data.
        
        subdf = self.selected_subdf()
        if len( subdf.index ) > 0:
            identities = list( subdf.index.astype(str) )
            self.SEND_CONTENTS.emit( identities, self._settings )
        else:
            log.debug( 'no selection, nothing to send' )
            
#---------------------------------------------------------------------------+++
# end 2023.10.12
# update drag/drop
