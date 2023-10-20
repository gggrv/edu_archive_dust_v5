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
from sparkling.grimoire.PlaylistColumns import (
    ColumnsPlaylist,
    NODE, DB_DEFAULT,
    LABEL_SEPARATOR, MULTIVALUE_SEPARATOR
    )
# gui
from sparkling.common.pyqt5.PandasTableView import PandasTableView
from sparkling.common.pyqt5.parentless.DfEditor import DfEditor
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions
# common
from sparkling.common import ( unique_loc, delrem )
from sparkling.common.pyqt5 import ( mime2file )
# emuns
from sparkling.common.enums.Consent import EConsent

def _open_path( df, dirname=False ):
    
    # Starts a file/folder with standard os methods.
    
    c = ColumnsPlaylist
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
    
    c = ColumnsPlaylist
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

def _parse_path( path ):
    
    c = ColumnsPlaylist
        
    param_dict = {
        c.path: path,
        c.title: os.path.basename(path),
        }
        
    return param_dict

class NodeViewer( PandasTableView ):
    
    # I expect that this widget is used to display
    # some `nodes` from a single `db`.
    # Logical purpose of these `nodes` may vary,
    # tools to browse/edit them should be uniform.

    # invisible spawned parentless windows will be saved here
    _parentless_windows = None # future list
    
    # connection to neo4j server
    # should be provided/updated by host
    _conn = None
    
    # which tool to use to edit nodes
    _node_editor_class = None
    
    # future dictionary
    # i can write anything i want, but for the sake
    # of compatibility and flexibility i will be using
    # `ColumnsPlaylist` format
    # i expect `settings` to be fully validated beforehand
    _settings = None
    
    def __init__( self,
                  parent=None,
                  node_editor_class=DfEditor,
                  accept_drops=True,
                  *args, **kwargs ):
        super( NodeViewer, self ).__init__(
            parent=parent, *args, **kwargs )
        
        # remember
        self._settings = {}
        self._parentless_windows = []
        self._node_editor_class = node_editor_class
        
        # appearance
        self.setWordWrap( False )
        self.setAcceptDrops( accept_drops )
        self.setContextMenuPolicy( Qt.ActionsContextMenu )
        
        # interactions
        self.__init_context_menu()
        
    def __init_context_menu( self ):
        
        # Called once during init.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        actions = [
             {
                 c.identity: 'grimoire/node_viewer/row/edit',
                 c.text: 'Edit',
                 c.method: self.launch_selection_editor,
                 c.shortcut: 'Alt+Return',
                 },
            {
                c.identity: 'grimoire/node_viewer/row/del_from_view',
                c.text: 'Remove',
                c.method: self.del_from_view,
                c.shortcut: 'Del',
                },
            {
                c.identity: 'grimoire/node_viewer/row/del_from_db',
                c.text: 'Delete from database',
                c.method: self.del_from_view_db,
                c.shortcut: 'Alt+Shift+Down',
                c.enabled: False,
                c.visible: False,
                },
            {
                c.identity: 'grimoire/node_viewer/row/del_from_disk',
                c.text: 'Delete from database and disk',
                c.method: self.del_from_view_db_disk,
                c.shortcut: 'Alt+Down',
                },
            ]
        
        c.add_actions( self, actions )
        
    def set_settings( self, settings ):
        
        # It's the same as setting `playlist` in the
        # upgraded subclasses.
        
        self._settings = {} if settings is None else settings
        
        c = ColumnsPlaylist
        
        if c.forbid_deep_deletions in settings:
            # TODO
            # custom editing widget
            c.validate_deep_deletions( settings )
            forbid = True if settings[c.forbid_deep_deletions]==EConsent.CONSENT else False
            self.forbid_deep_deletions( forbid )
        
    def settings( self ):
        # For external use only.
        return self._settings
        
    def set_connection( self, conn ):
        self._conn = conn
        
    def the_dying_message( self ):
        # Whenever this widget/subclass is no longer needed,
        # I may want to remember certain things.
        pass
    def destroy( self, *args, **kwargs ):
        self.the_dying_message()
        super( NodeViewer, self ).destroy( *args, **kwargs )
    def deleteLater( self ):
        self.the_dying_message()
        super( NodeViewer, self ).deleteLater()
    def closeEvent( self, ev ):
        self.the_dying_message()
        super( NodeViewer, self ).closeEvent( ev )
        
    def launch_selection_editor( self, constructor_parameters=None ):
        
        # Launches editor.
        
        # make sure i have editor tool
        if self._node_editor_class is None:
            log.error( 'no editor specified, can\'t edit' )
            return
        
        # make sure i have settings
        if self._settings is None:
            log.error( 'no viewer settings, can\'t edit' )
            return
        
        # make sure i have rows to edit
        subdf = self.selected_subdf()
        if len(subdf.index)==0: return
        
        # short name for convenience
        c = ColumnsPlaylist
        ce = self._node_editor_class.ColumnsConstructor
        
        # define custom parameters
        # attempt to set master column to path
        # may fail
        # TODO
        # external file with preferences
        # for each db and label
        ps = {} if constructor_parameters is None else constructor_parameters
        ps.update({
            ce.df: subdf,
            ce.display_vertical: False,
            ce.db_name: self._settings[c.db_name]
            })
        
        w = self._node_editor_class( ps, parent=None )
        w.EDITING_FINISHED.connect( self._accept_selection_edits_event )
        
        self._register_parentless_window(w)
        w.show()
        
    def _accept_selection_edits_event( self, changes, db_name ):
        
        # Happens whenever I change node values.
        # The view itself remains the same,
        # but data in the database should update.
        
        # detect what am i working with
        old_value, new_value = changes
        old_df, new_df = None, None
        old_s, new_s = None, None
        if type(old_value) == pd.DataFrame: old_df=old_value
        elif type(old_value) == pd.Series: old_s=old_value
        if type(new_value) == pd.DataFrame: new_df=new_value
        elif type(new_value) == pd.Series: new_s=new_value
        
        is_df_and_df = not old_df is None and not new_df is None
        is_s_and_s = not old_s is None and not new_s is None
        #is_df_and_s = not old_df is None and not new_s is None
        #is_s_and_df = not old_s is None and not new_df is None
        
        if is_df_and_df: # i have two dataframes
            # completely replace old with the new one
        
            # make sure i have rows to work with
            have_same_length = len(old_df.index) == len(new_df.index)
            have_some_rows = len(old_df.index)>0
            if not ( have_same_length and have_some_rows ):
                log.error( f'failed to apply changes after editing the df - content length mismatch: expected {len(old_df.index)}, got {len(new_df.index)}' )
                return
            if old_df.equals(new_df):
                log.info( 'the df was not edited - no changes detected, not doing anything' )
                return
                
            # change in the same database
            # the editor thinks i'm at
            self._conn.replace_nodes( new_df, db_name )
                
            # change in view
            self.replace_subdf( new_df )
            
            # no need to change in `playlist contents` because
            # shown identities did not change
            
            # i may need this in a child class
            return new_df
        
        elif is_s_and_s: # i have two series
            # completely replace old with the new one
            # make sure i have rows to work with
            have_same_length = len(old_s.index) == len(new_s.index)
            have_some_rows = len(old_s.index)>0
            if not ( have_same_length and have_some_rows ):
                log.error( f'failed to apply changes after editing the df - content length mismatch: expected {len(old_s.index)}, got {len(new_s.index)}' )
                return
            if old_s.equals(new_s):
                log.info( 'the df was not edited - no changes detected, not doing anything' )
                return
            if not type( new_s.index ) == pd.core.indexes.numeric.Int64Index:
                log.info( 'this kind of series is not supported yet' )
                raise NotImplementedError
            
            new_df = self._MODEL.df.loc[ new_s.index ]
            new_df[ new_s.name ] = new_s
            self._conn.replace_nodes( new_df, db_name )
            self.replace_subdf( new_df )
            
            # i may need this in a child class
            return new_df
        
        else:
            
            raise NotImplementedError
            
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
            c.identity: 'grimoire/node_viewer/row/del_from_db',
            c.enabled: not forbid,
            c.visible: not forbid,
            },
        {
            c.identity: 'grimoire/node_viewer/row/del_from_disk',
            c.enabled: not forbid,
            c.visible: not forbid,
            },
        {
            c.identity: 'grimoire/node_viewer/row/del_from_disk',
            c.enabled: not forbid,
            c.visible: not forbid,
            },
        ]
        
        c.modify_actions( self, modifications )
    
    def del_from_view( self ):
        
        # I want to remove specific rows from current view
        # without modifying `db`.
        # This method should be overridden.
        
        self.delete_selection()
        
    def del_from_view_db( self ):
        
        # I want to delete rows from db and current view.
        # For more controlled and faster use, rather then
        # subsequently calling `del_from_view`,
        # `del_from_db`, `del_from_disk`, I implement each
        # functionality independently.
        
        # make sure i have something to work with
        rowilocs = self.selected_rowilocs()
        if len(rowilocs)==0: return
        
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.db_name in self._settings:
            log.error( 'i need db_name in order to delete items in df, can\'t do anything' )
            return
        
        # ask confirmation
        msg = QMessageBox()
        msg.setWindowTitle( 'Delete?' )
        msg.setStandardButtons(
            QMessageBox.Ok
            |QMessageBox.Cancel
            )
        msg.setDefaultButton( QMessageBox.Cancel )
        msg.setText( 'Selected rows will be \n- deleted from db\nAre you sure?' )
        retval = msg.exec_()
        if retval==QMessageBox.Cancel: return
        
        # del from db
        subdf = self._MODEL.df.iloc[rowilocs]
        identities = list( subdf.index )
        query = f'MATCH ({NODE}) WHERE ID({NODE}) IN {identities} DETACH DELETE {NODE}'
        response = self._conn.query( query, db_name=self._settings[c.db_name] )
        if response is None:
            log.error( 'failed to delete from server' )
            return
        
        # del from view
        self.delete_rows( rowilocs )
        self.select_next_row( rowilocs[0] )
        
    def del_from_view_db_disk( self ):
        
        # I want to delete rows from disk, db and current view.
        
        # make sure i have something to work with
        rowilocs = pd.Series( self.selected_rowilocs() )
        if len(rowilocs)==0: return
        
        # short name for convenience
        c = ColumnsPlaylist
        
        if not c.db_name in self._settings:
            log.error( 'i need db_name in order to delete items in df, can\'t do anything' )
            return
        
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
        response = self._conn.query( query, db_name=self._settings[c.db_name] )
        if response is None:
            log.error( 'failed to delete from server' )
            return
        
        # del from view
        self.delete_rows( rowilocs )
        self.select_next_row( rowilocs[0] )
        
    def _register_parentless_window( self, w ):
        
        # I operate with many parentless windows.
        # They would disappear if no one referenced them.
        # Here I save those references.
    
        w.setObjectName(
            '%s%s'%( w.objectName(), unique_loc() )
            )
        w.OK_TO_CLOSE.connect( self._remove_parentless_window_event )
        self._parentless_windows.append(w)

    def _remove_parentless_window_event( self, object_name ):
        
        # I no longer need this parentless dialog.
        # I destroy the object and
        # remove reference to it from self.dialogs.

        for iloc, w in enumerate(self._parentless_windows):
            
            if w.objectName()==object_name:

                self._parentless_windows.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                # just die already
                return
        
    def dragEnterEvent( self, ev ):
        
        # Node viewer should be able to accept
        # various drag and drops.
        
        c = ColumnsPlaylist
        
        # make sure this playlist supports adding items
        if c.auto_query in self._settings:
            # this playlist is rule-based,
            # i don't want to edit it manually
            log.error( 'this playlist is automatic, i don\'t want to add items to it manually' )
            ev.ignore()
            return
        
        ev.accept()
    
    def dragMoveEvent( self, ev ):
        
        ev.accept()

    def dropEvent( self, ev ):
        
        if ev.mimeData().hasUrls():
            # got some links
            
            is_some_url = r'://' in ev.mimeData().text()
            is_local_path = ev.mimeData().text().startswith( r'file://' )
            if is_local_path or is_some_url:
                # these links are ok
                
                paths = mime2file( ev.mimeData() ) \
                    if is_local_path \
                    else ev.mimeData().text().split('\n')
                    
                self._add_to_view_db( paths, False, parsing_function=_parse_path )
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
        
    def _add_to_view_db( self, items, already_parsed,
        parsing_function=None ):
        
        # I can call this method whenever I want my
        # playlist to accept new somethings and save them to db.
        # For careful programmatic use only.
        
        c = ColumnsPlaylist
        
        # foolcheck
        if not c.db_name in self._settings:
            log.error( 'can\'t accept because no db name specified' )
            return
        if not type(items) in [ list, set ]:
            log.error( 'can\'t accept because i need an iterable' )
            return
        
        db_name = self._settings[c.db_name]
        identities = []
        for item in items:
            
            # auto parse according to user preferences
            if already_parsed:
                param_dict = item
            else:
                if parsing_function is None:
                    param_dict = { c.title:item }
                else:
                    param_dict = parsing_function( item )
            
            # send to db
            node = ColumnsPlaylist.convert_node( NODE, '', param_dict=param_dict )
            response = self._conn.query(
                f'CREATE {node} RETURN toString(ID({NODE})) AS identity',
                db_name=db_name
                )
            
            if response is None:
                log.error( f'failed to connect to server to create node {node} in db {db_name}' )
            else:
                for record in response:
                    identities.append( record['identity'] )
                    
        # update settings
        c.add_identities( self._settings, identities )
        
        # TODO
        # there is no need to redownload the whole contents
        # in order to display added items -
        # partially download only necessary data
        self.set_settings( self._settings )
            
    def add_rows( self, rows ):
        
        # if i want to use this method,
        # i need to decide on approach
        # 1) upload `rows` to db, return records, convert them to df with correct df.index
        # 2) parse existing fields, convert them to df with correct df.index
        
        # currently it will mess up rowilocs and
        # self._MODEL.df.index,
        # so i forbid it for now
        
        raise NotImplementedError
            
#---------------------------------------------------------------------------+++
# end 2023.10.19
# fix del from disk
