# -*- coding: utf-8 -*-
#Python class "DfEditor". Allows to conveniently edit any pandas.DataFrame via PyQt5 GUI. Copyright (C) 2022 Anna Anikina
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
import os # needed for gui parser input eval
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QVBoxLayout, QListWidget, QWidget,
    QHBoxLayout, QPushButton, QSplitter, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QLineEdit, QCompleter, QStyledItemDelegate )
# same project
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions, BaseColumns
from sparkling.common import unique_loc

_MULTIPLE_VALUES_INDICATOR = '<MULTIPLE VALUES>'
_MULTIPLE_VALUES_SEPARATOR = '; '
_MAXIMUM_MULTIPLE_VALUES = 10 # items

class ColumnsDfEditorConstructor( BaseColumns ):
    
    completions_dictionary = 'completions_dictionary'
    
    # which `pandas.DataFrame` to edit
    df = 'df'
    db_name = 'db_name'
    
    # layout columns style: vertical/horizontal
    display_vertical = 'display_vertical'
    
    master_column = 'master_column'
    
    @staticmethod
    def validate_constructor_parameters( ps ):
        
        # In order to reduce number of human errors,
        # this function provides an option to
        # manually check `constructor parameters` 
        # and enforce corrections before
        # sending them to the `constructor`.
        
        # short name for convenience
        c = ColumnsDfEditorConstructor
        
        # make sure `df` field is either valid
        # or absent
        if c.df in ps:
            if ps[c.df] is None:
               ps.pop( c.df )

def df2series( df ):

    # Transforms source dataframe info 2-columned df:
    # column_name, concatenated_values.
    
    df = df.fillna('')
    
    if len(df)==0:
        return pd.Series()

    texts = []
    
    for col in df.columns:
        
        values = list( df[col].astype(str).unique() )
        if len( values )==1:
            texts.append( values[0] )
        else:
            values.insert( 0, _MULTIPLE_VALUES_INDICATOR )
            
            stop = _MAXIMUM_MULTIPLE_VALUES \
                if len(values)>_MAXIMUM_MULTIPLE_VALUES \
                else len(values)
            
            texts.append(
                _MULTIPLE_VALUES_SEPARATOR.join(values[:stop])
                )

    return pd.Series( data=texts, index=df.columns )

class CustomDelegate( QStyledItemDelegate ):
    
    # help:
    # https://stackoverflow.com/questions/66543574/how-to-have-auto-completer-in-a-qtablewidget-cell-that-newly-created-in-pyqt5
    
    __completers = None
    
    def __init__( self,
                  completions_dictionary,
                  parent=None,
                  *args, **kwargs ):
        super( CustomDelegate, self ).__init__( parent=parent, *args, **kwargs )
            
        self.__completers = {}
        
        if not type(completions_dictionary) == dict:
            return
        
        for col, completions in completions_dictionary.items():
            
            completer = QCompleter( completions, parent=self )
            completer.setCaseSensitivity( Qt.CaseInsensitive )
            completer.setFilterMode( Qt.MatchContains )
            self.__completers[col] = completer

    def createEditor( self, parent, option, index ):
        
        editor = QLineEdit( parent=parent )
        
        coliloc = index.column()
        
        if coliloc in self.__completers:
            editor.setCompleter( self.__completers[coliloc] )
            
        return editor
    
class DfEditor( QWidget ):
    
    # Has two columns, allows to edit one pd.Dataframe.
    
    ColumnsConstructor = ColumnsDfEditorConstructor
    
    # TODO
    # dedicated tableview and model
    # for more control over the data
    
    # TODO
    # remember splitter positions
    # allow to switch between horizontal and vertical from gui
    
    OK_TO_CLOSE = pyqtSignal( str )
    EDITING_FINISHED = pyqtSignal( tuple, str )
    
    _RIGHT_COLUMN_WIDTH = 530
    
    class Strings:
        
        WINDOW_TITLE = 'Entry editor'
        
        BT_OK = 'Ok'
        BT_APPLY = 'Apply'
        BT_CANCEL = 'Cancel'
        
        ADD_FIELD = 'Add field'
        DELETE_FIELD = 'Delete selected fields'
        
        DELETE_CONFIRMATION_TITLE = 'Delete selecetd fields for all items?'
        DELETE_CONFIRMATION_TEXT = 'Even unselected items will lose these values.'
        
        LVAL_TEXT = 'None / any field name'
        RVAL_TEXT = 'self.df[\'column_name\'], press RETURN for preview'
    
    class Gui:
    
        master_column_cbx = None
        list_widget = None
        main_table = None
        bottom_vbox = None
        parse_rval = None
        parse_lval = None
        parse_preview = None
        
    # my edits
    # i want to access them directly
    # from gui
    # in the parsable command input section
    db_name = None
    df = None
    _old_df = None # copy for comparison and output
    
    # which column values are displayed in the list view
    _master_column = None
    
    _completions_dictionary = None
    
    __display_vertical = False

    def __init__( self,
                  constructor_parameters,
                  parent=None,
                  *args, **kwargs ):
        super( DfEditor, self ).__init__( parent=parent, *args, **kwargs )
        
        # short name for convenience
        c = ColumnsDfEditorConstructor
        ps = constructor_parameters
        
        if not c.db_name in ps:
            raise NotImplementedError
        self.db_name = ps[c.db_name]
        
        # list above table / side by side
        if c.display_vertical in ps:
            self.__display_vertical = ps[c.display_vertical]
        
        if c.completions_dictionary in ps:
            self._completions_dictionary = ps[c.completions_dictionary]
        
        self.setWindowTitle( DfEditor.Strings.WINDOW_TITLE )
        self.resize( 1000, 880 )
        
        # set dataframes
        # i can have empty ones - i can create necessary columns
        # from scratch
        if c.df in ps:
            self.df = ps[c.df]
            self._old_df = self.df.copy()
        else:
            self.df = pd.DataFrame()
            self._old_df = pd.DataFrame()

        split_vmid = QSplitter(
            Qt.Vertical if self.__display_vertical else Qt.Horizontal,
            parent=self
            )

        # layout
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0,0,0,0)

        # top

        top_widget = QWidget( parent=self )
        top_vbox = QVBoxLayout()
        
        self.Gui.master_column_cbx = QComboBox( parent=self )

        self.Gui.list_widget = QListWidget( parent=self )
        self.Gui.list_widget.setSelectionMode(
            QListWidget.ExtendedSelection
            )
        
        top_vbox.addWidget( self.Gui.master_column_cbx )
        top_vbox.addWidget( self.Gui.list_widget )
        
        top_widget.setLayout( top_vbox )

        # fields
        
        self.Gui.main_table = QTableWidget( parent=self )
        self.Gui.main_table.setContextMenuPolicy( Qt.ActionsContextMenu )
        
        self.Gui.main_table.setItemDelegate(
            CustomDelegate(
                self._completions_dictionary,
                parent=self.Gui.main_table )
            )
        
        # bottom
        
        parser_hbox = QHBoxLayout()
        self.Gui.parse_lval = QLineEdit( parent=self )
        self.Gui.parse_rval = QLineEdit( parent=self )
        self.Gui.parse_preview = QListWidget( parent=self )
        
        self.Gui.parse_lval.setPlaceholderText(
            DfEditor.Strings.LVAL_TEXT )
        self.Gui.parse_rval.setPlaceholderText(
            DfEditor.Strings.RVAL_TEXT )
        
        self.Gui.parse_preview.setVisible( False )
        
        parser_hbox.addWidget( self.Gui.parse_lval )
        parser_hbox.addWidget( self.Gui.parse_rval )
        
        # confirmation

        controls_hbox = QHBoxLayout()

        bt_ok = QPushButton( parent=self )
        bt_ok.setObjectName( 'bt_ok' )
        bt_ok.setText( DfEditor.Strings.BT_OK )

        bt_no = QPushButton( parent=self )
        bt_no.setObjectName( 'bt_no' )
        bt_no.setText( DfEditor.Strings.BT_CANCEL )

        bt_apply = QPushButton( parent=self )
        bt_apply.setObjectName( 'bt_apply' )
        bt_apply.setText( DfEditor.Strings.BT_APPLY )

        controls_hbox.addWidget( bt_apply )
        controls_hbox.addWidget( bt_ok )
        controls_hbox.addWidget( bt_no )
        
        # other

        # assemble

        main_widget = QWidget( parent=self )
        main_vbox = QVBoxLayout()
        
        main_vbox.addWidget( self.Gui.main_table )
        main_vbox.addLayout( parser_hbox )
        main_vbox.addWidget( self.Gui.parse_preview )
        
        main_widget.setLayout( main_vbox )
        
        
        
        
        split_vmid.addWidget( top_widget )
        split_vmid.addWidget( main_widget )
        
        # set default middle splitter position
        if self.__display_vertical:
            split_vmid.setStretchFactor( 0,1 )
            split_vmid.setStretchFactor( 1,5 )
        else:
            split_vmid.setStretchFactor( 0,3 )
            split_vmid.setStretchFactor( 1,7 )
        
        lyt.addWidget( split_vmid )
        lyt.addLayout( controls_hbox )
        self.setLayout( lyt )

        # autorun
        
        bt_ok.clicked.connect( self._press_ok_event )
        bt_no.clicked.connect( self.close )
        bt_apply.clicked.connect( self.__send_changes_to_db_event )
        
        # i changed master column
        self.Gui.master_column_cbx.currentTextChanged.connect(
            self._master_column_changed_event )
        
        # i want to refresh main table
        self.Gui.list_widget.itemSelectionChanged.connect(
            self._list_widget_selection_changed_event
            )
        
        self.Gui.main_table.itemChanged.connect(
            self._accept_user_changes_to_df_event )
        
        # parser controls
        
        self.Gui.parse_rval.editingFinished.connect(
            self._preview_parsable_command_event )
        
        # other
        
        self._init_context_menu()
        
        self._populate_master_cbx()
        self._master_column_changed_event(
            self.Gui.master_column_cbx.currentText() )
        
        self.select_all()
        
        if c.master_column in ps:
            self.set_master_column( ps[c.master_column] )
        
    def _init_context_menu( self ):
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        actions = [
            {
                c.identity: 'common/dfeditor/edit/add_field',
                c.text: DfEditor.Strings.ADD_FIELD,
                c.shortcut: 'Ctrl+N',
                c.method: self._new_column,
                },
            {
                c.identity: 'common/dfeditor/edit/delete_field',
                c.text: DfEditor.Strings.DELETE_FIELD,
                c.shortcut: 'Del',
                c.method: self._delete_field,
                },
            ]
        
        c.add_actions( self.Gui.main_table, actions )
        
    def set_master_column( self, new_master_column ):
        
        if not new_master_column in self.df.columns:
            log.error( f'selected master column {new_master_column} is not available in the df: {self.df.columns}' )
            return
        
        # make sure current text in cbx is matching
        # because i can call this function from anywhere
        current_text = self.Gui.master_column_cbx.currentText()
        if not current_text == new_master_column:
            # aha! they differ
            self.Gui.master_column_cbx.blockSignals( True )
            self.Gui.master_column_cbx.setCurrentText( new_master_column )
            self.Gui.master_column_cbx.blockSignals( False )
            
        self._master_column = new_master_column

        # reapply current selection
        rowilocs = self.get_selected_rowilocs()
        self._populate_top_list()
        self.select_rows( rowilocs )
        
    def refresh_selector_section( self, new_master_column=None ):
        
        # Refreshes data in the section with
        # master cbx and list view.
        
        self._populate_master_cbx()
        
        if new_master_column is None:
            # reapply current
            self.set_master_column( self._master_column )
        else:
            # set new
            self.set_master_column( new_master_column )
        
    def _new_column( self ):
        
        # column name must start not with a number
        col = 'a%s' % unique_loc()
        self.df[ col ] = pd.NA
        
        self.refresh_selector_section()
        
        # make sure rows have appropriate height
        font_height = self.Gui.main_table.fontMetrics().height()
        for rowiloc in range( self.Gui.main_table.rowCount() ):
            self.Gui.main_table.setRowHeight( rowiloc, font_height )
        
    def _delete_field( self ):
        
        # Deletes currently selected field for all top list items
        # and selects next field.
        
        indexes = self.Gui.main_table.selectedIndexes()
        if len( indexes )==0: return
        
        # ask confirmation
        msg = QMessageBox()
        msg.setWindowTitle( DfEditor.Strings.DELETE_CONFIRMATION_TITLE )
        msg.setText( DfEditor.Strings.DELETE_CONFIRMATION_TEXT )
        msg.setStandardButtons(
            QMessageBox.Ok
            |QMessageBox.Cancel
            )
        msg.setDefaultButton( QMessageBox.Cancel )
        retval = msg.exec_()
        if retval==QMessageBox.Cancel: return
        
        rowilocs = [ i.row() for i in indexes ]
        
        cols2drop = []
        for rowiloc in rowilocs:
            col = self.Gui.main_table.item( rowiloc, 0 ).text()
            cols2drop.append(col)
        self.df.drop( columns=cols2drop, inplace=True )
        
        # remove from current view backwards
        # in a separate cycle so as not to mess up rowilocs
        for rowiloc in rowilocs[::-1]: # start from last, go up
            self.Gui.main_table.removeRow( rowiloc )
        
        last_row = self.Gui.main_table.rowCount()-1
        self.Gui.main_table.selectRow(
            rowilocs[0] if rowilocs[0]<last_row else last_row )
    
        self.refresh_selector_section()
        
    def _populate_master_cbx( self, sort=False, sort_asc=True ):
        
        # Does not trigger anything.
        # I want master_cbx to accurately show all
        # existing df columns.
        
        self.Gui.master_column_cbx.blockSignals( True )
        self.Gui.master_column_cbx.clear()
        
        texts = [ str(v) for v in self.df.columns ]
        if sort:
            texts = list(
                pd.Series( texts ).sort_values( ascending=sort_asc )
                )
            
        self.Gui.master_column_cbx.addItems( texts )
        self.Gui.master_column_cbx.blockSignals( False )
        
    def _populate_top_list( self ):
        
        # Does not trigger anything.
    
        if self.df.columns.size==0: # no columns
        
            if len( self.df )==0: # no rows
                log.error( 'current df has no rows or columns, so list items look empty' )
                return
            
            # some rows
            
            self.Gui.list_widget.blockSignals( True )
            self.Gui.list_widget.clear()
            texts = [ f'ROW № {iloc}' for iloc in range( len(self.df) ) ]
            self.Gui.list_widget.addItems( texts )
            self.Gui.list_widget.blockSignals( False )
        
            log.error( 'current df has rows, but no columns, so list items are filled with placeholder' )
            return

        # some rows and columns

        self.Gui.list_widget.blockSignals( True )
        self.Gui.list_widget.clear()
        
        texts = list(
            self.df[self._master_column].fillna( '', inplace=False )
            )
        self.Gui.list_widget.addItems( texts )
        
        self.Gui.list_widget.blockSignals( False )
        
    def _master_column_changed_event( self, new_master_column ):
        self.set_master_column( new_master_column )
        
    def _accept_user_changes_to_df_event( self, item ):
        
        rowiloc = self.Gui.main_table.currentRow()
        coliloc = self.Gui.main_table.currentColumn()
        
        if coliloc==0:
            
            # this is column name
            # i renamed df column
            
            columns = [
                self.Gui.main_table.item(iloc,0).text() \
                for iloc in range( self.Gui.main_table.rowCount() )
                ]
            
            self.df.columns = columns
            self._populate_master_cbx()
            self._master_column_changed_event( self._master_column )
        
        elif coliloc==1:
            
            # this is text
            # i changed value
            # i want to set this value to current subdf
            
            loc = self.Gui.main_table.item( rowiloc, 0 ).text()
            value = item.text()
            if len(value)==0: value=pd.NA
            
            subdf_index = self.df.iloc[
                self.get_selected_rowilocs() ].index
        
            self.df.loc[subdf_index,loc] = value
    
    def select_all( self ):
        
        # Efficiently selects rows without triggering
        # exessive events.
    
        count = self.Gui.list_widget.count()
        if count==0:
            # no rows, nothing to select
            return
        
        # select all but the last row
        # without triggering anything
        self.Gui.list_widget.blockSignals( True )
        
        for iloc in range(count-1): # skip last
            self.Gui.list_widget.item(iloc).setSelected( True )
        
        self.Gui.list_widget.blockSignals( False )
        
        # select last row and trigger something
        self.Gui.list_widget.item(count-1).setSelected( True )
            
    def select_rows( self, rowilocs ):
        
        # Efficiently selects rows without triggering
        # exessive events.

        count = self.Gui.list_widget.count()
        if count==0:
            # no rows, nothing to select
            return
            
        if len(rowilocs)==0:
            # no rows, nothing to select
            return
        if len(rowilocs)==1:
            self.Gui.list_widget.item( rowilocs[0] ).setSelected( True )
            return
    
        # select all but the last row
        # without triggering anything
        
        self.Gui.list_widget.blockSignals( True )
        
        for iloc in range( count ):
            if iloc in rowilocs[:-1]: # skip last
                self.Gui.list_widget.item(iloc).setSelected( True )
            
        self.Gui.list_widget.blockSignals( False )
        
        # select last row and trigger something
        self.Gui.list_widget.item( rowilocs[-1] ).setSelected( True )
            
    def get_selected_rowilocs( self ):
        
        rowilocs = []
        for iloc in range( self.Gui.list_widget.count() ):
            if self.Gui.list_widget.item(iloc).isSelected():
                rowilocs.append( iloc )
                
        return rowilocs
            
    def _list_widget_selection_changed_event( self ):

        # This event is triggered whenever I
        # change the list_widget selection.

        rowilocs = self.get_selected_rowilocs()

        # i want to update main table with data from
        # selected items

        self._populate_main_table(
            self.df.iloc[rowilocs]
            )
        
    def _populate_main_table( self, subdf, hidden_colilocs=None ):
        
        self.Gui.main_table.blockSignals( True )
        self.Gui.main_table.clear()
        
        # they reset every time i clear it
        self.Gui.main_table.setHorizontalHeaderLabels( [ 'Name', 'Value' ] )
        
        s = df2series( subdf )
        
        # row and column count should be set before item creation
        self.Gui.main_table.setRowCount( s.count()  )
        self.Gui.main_table.setColumnCount( 2 )
        
        rowiloc = 0
        for loc, text in s.iteritems():
            self.Gui.main_table.setItem( rowiloc, 0, QTableWidgetItem(loc) )
            self.Gui.main_table.setItem( rowiloc, 1, QTableWidgetItem(text) )
            rowiloc += 1
        
        self.Gui.main_table.setColumnWidth( 1, self._RIGHT_COLUMN_WIDTH )
        
        # make sure rows have appropriate height
        font_height = self.Gui.main_table.fontMetrics().height()
        for rowiloc in range( self.Gui.main_table.rowCount() ):
            self.Gui.main_table.setRowHeight( rowiloc, font_height )
            
        self.Gui.main_table.blockSignals( False )
        
    def __send_changes_to_db_event( self, ev ):
        self.EDITING_FINISHED.emit(
            ( self._old_df, self.df ), self.db_name
            )
    
    def _press_ok_event( self, ev ):
        self.__send_changes_to_db_event( None )
        self.close()

    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
        
    def _preview_parsable_command_event( self ):
        
        # what to do (must be present)
        command = self.Gui.parse_rval.text()
        if len(command)==0:
            self.Gui.parse_preview.setVisible( False )
            return
        
        # whom to apply (may be empty)
        col = self.Gui.parse_lval.text()
        
        self.Gui.parse_preview.clear()
        
        try:
            
            # preview right hand value
            valueR = eval(command)
            self.Gui.parse_preview.setVisible( True )
            self.Gui.parse_preview.addItems( valueR )
            
            # apply left hand value
            if len(col)>0:
                self.Gui.parse_lval.clear()
                self.Gui.parse_preview.setVisible( False )
                self.df[col] = valueR
                self._list_widget_selection_changed_event()
                
        except Exception as ex:
            
            self.Gui.parse_preview.setVisible( True )
            self.Gui.parse_preview.addItems( str(ex).split('\n') )

#---------------------------------------------------------------------------+++
# end 2022.10.21
# BaseColumns
