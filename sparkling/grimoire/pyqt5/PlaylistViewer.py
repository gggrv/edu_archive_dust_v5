# -*- coding: utf-8 -*-
#Python utility "Grimoire Playlist Viewer". Allows to view the contents of a "playlist Neo4J node" via PyQt5. Copyright (C) 2023 Anna Anikina
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------+++

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
    NODE, DB_DEFAULT,
    MULTIVALUE_SEPARATOR
    )
# gui
from sparkling.grimoire.pyqt5.NodeViewer import NodeViewer, ColumnsActionDefinitions, _open_path, DfEditor
from sparkling.common.pyqt5 import ( get_QItemSelection_rowilocs )
# common

PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR = [
    ColumnsPlaylist.identity,
    ColumnsPlaylist.db_name
    ]

class PlaylistViewer( NodeViewer ):

    SEND_CONTENTS = pyqtSignal( list, dict )
    OVERRIDE_SETTINGS = pyqtSignal( dict )
    REQUEST_PLUGINS_ENABLE = pyqtSignal( str, NodeViewer )
    REQUEST_PLUGINS_DISABLE = pyqtSignal( str, NodeViewer )
    
    # which tool to use to rename nodes
    _file_renamer_class = None
    
    def __init__( self,
                  selection_changed_event=True,
                  node_editor_class=DfEditor,
                  file_renamer_class=None,
                  accept_drops=True,
                  manually_reorder_rows=True,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistViewer, self ).__init__(
            node_editor_class=node_editor_class,
            accept_drops=accept_drops,
            manually_reorder_rows=manually_reorder_rows,
            parent=parent, *args, **kwargs )
        
        # remember
        self._file_renamer_class = file_renamer_class
        
        # appearance
        self.setWordWrap( False )
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
            
        #if sorted_event:
        #    # these signals were suggested by an AI assistant
        #    #self.horizontalHeader().sectionClicked.connect( self.__horizontal_section_clicked_event )
        #    self.horizontalHeader().sortIndicatorChanged.connect( self.__horizontal_sorting_indicator_changed_event )
        
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
        # I end up here when I decide to somehow change
        # contents of a currently open playlist.
        # `Currently open` means `unique object instance exists`.
        
        c = ColumnsPlaylist
        
        # compile a list of plugin changes
        to_remove, to_add = c.get_plugin_changes( self._settings, settings )
        if not to_remove=='':
            self.REQUEST_PLUGINS_DISABLE.emit( to_remove, self )
        
        # do what needs to be done
        super( PlaylistViewer, self ).set_settings( settings )
        
        # additinally i need to populate this viewer with
        # downloaded nodes
        
        # download contents from db and add them to view
        
        query = c.get_contents_query( self._settings )
        if query is None:
            # this playlist is empty at this moment
            # and i can manually set auto query / add items
            # from search
            columns_to_hide = self._settings[ColumnsPlaylist.columns_to_hide].split(MULTIVALUE_SEPARATOR) if ColumnsPlaylist.columns_to_hide in self._settings else PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR
            appropriate_reverse = False
            if ColumnsPlaylist.columns_to_show in self._settings:
                columns_to_hide = self._settings[ColumnsPlaylist.columns_to_show].split(MULTIVALUE_SEPARATOR)
                appropriate_reverse = True
            self.switch_df( pd.DataFrame(), columns_to_hide=columns_to_hide, appropriate_reverse=appropriate_reverse )
            
            # request plugins
            if not to_add=='':
                self.REQUEST_PLUGINS_ENABLE.emit( to_add, self )
            
            return
            
        response = self._conn.query( query, db_name=self._settings[c.db_name] )
        
        if response is None:
            # TODO
            # pop-up with log messages
            log.error( 'query most likely failed, please review db settings manually' )
            return
                
        df = pd.DataFrame([ r[NODE] for r in response ])
        df.index = [ r[NODE].id for r in response ]
        df.fillna( '', inplace=True )
        ColumnsPlaylist.fill_reserved_columns( self._conn, df, db_name=self._settings[c.db_name] )
        
        if c.identities in self._settings:
            # enforce specific row ordering
            # TODO
            # do so in Columns
            # help:
            # https://stackoverflow.com/questions/30009948/how-to-reorder-indexed-rows-based-on-a-list-in-pandas-data-frame
            if not self._settings[c.identities].strip() == '':
                df = df.reindex([ int(loc) for loc in self._settings[c.identities].split(' ') ])
        
        columns_to_hide = self._settings[ColumnsPlaylist.columns_to_hide].split(MULTIVALUE_SEPARATOR) if ColumnsPlaylist.columns_to_hide in self._settings else PLAYLIST_COLUMNS_TO_HIDE_IN_EDITOR
        appropriate_reverse = False
        if ColumnsPlaylist.columns_to_show in self._settings:
            columns_to_hide = self._settings[ColumnsPlaylist.columns_to_show].split(MULTIVALUE_SEPARATOR)
            appropriate_reverse = True
        self.switch_df( df, columns_to_hide=columns_to_hide, appropriate_reverse=appropriate_reverse )
        
        # request plugins
        if not to_add=='':
            self.REQUEST_PLUGINS_ENABLE.emit( to_add, self )
        
    def mouseDoubleClickEvent( self, ev ):
    
        # Reserved `PyQt5` method.
        
        if ev.button()==Qt.LeftButton:
            self._cm_open_file()
        
    def focusInEvent( self, ev ):
        
        # Reserved `PyQt5` method.
        
        # When this widget was clicked, it's internal `playlist`
        # became global `current active playlist`.
        # Now this functionality is deprecated.
        # Will keep this for future ideas.
        
        # help:
        # https://stackoverflow.com/questions/28793440/pyqt5-focusin-out-events
        
        super( PlaylistViewer, self ).focusInEvent( ev )
    
    def the_dying_message( self ):
        
        # Whenever this widget/subclass is no longer needed,
        # I may want to remember certain things.
        
        c = ColumnsPlaylist
        
        # remember item ordering
        self._settings[c.identities] = ' '.join(list( self._MODEL.df.index.astype(str) ))
        
        # notify playlist selector
        self.OVERRIDE_SETTINGS.emit( self._settings )
        
        super( PlaylistViewer, self ).the_dying_message()
        
    def launch_selection_editor( self ):
    
        constructor_parameters = {
            'master_column': ColumnsPlaylist.path,
            }
        
        super( PlaylistViewer, self ).launch_selection_editor( constructor_parameters=constructor_parameters )
        
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
        
    #def __horizontal_sorting_indicator_changed_event( self, coliloc, order ):
    #    
    #    # I end up here the moment before the table
    #    # is about to be sorted. Which means that this
    #    # method is currently useless.
    #
    #    c = ColumnsPlaylist        
    #
    #    # notify playlist selector
    #    self._settings[c.identities] = ' '.join(list( self._MODEL.df.index.astype(str) ))
    #    self.OVERRIDE_SETTINGS.emit( self._settings )
        
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
