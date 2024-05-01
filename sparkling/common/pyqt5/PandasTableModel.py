# -*- coding: utf-8 -*-
#Python class "Pandas TableModel". Allows to conveniently interface with a pandas.DataFrame via PyQt5 view/model architecture. Copyright (C) 2023 Anna Anikina
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
from natsort import index_natsorted
# pip install
from numpy import argsort
import pandas as pd
from PyQt5.QtCore import ( Qt, QAbstractTableModel )
# same project
from sparkling.common.enums.MimeTypes import EMimeTypes
from sparkling.common.BaseColumns import BaseColumns
            
class ColumnsMimeText( BaseColumns ):
    
    # Textual MimeData may be like this:
    # `key1=value1;key2=value2;`.
    
    #EQ = '='
    #SEP = ';'
    
    # i am dragging `df.index`, which allows to addess relevant
    # `df` rows using `loc`
    drag_df_locs = 'drag_df_locs'
    
    # i want to select specific rowilocs
    set_selected_rowilocs = 'set_selected_rowilocs'
    
#     @classmethod
#     def encode_into_text( cls, dictionary ):
#         items = []
#         for k, v in dictionary.items():    
#             item = f'{k}{cls.EQ}{v}'
#             items.append( item )
#         return cls.SEP.join( items )
        
#     @classmethod
#     def decode_into_dictionary( cls, text ):
#         dictionary = {}
#         for item in text.split( cls.SEP ):
#             k, v = item.split( cls.EQ, maxsplit=1 )
#             dictionary[k] = v
#         return dictionary

class PandasTableModel( QAbstractTableModel ):
    
    # will hold `pd.DataFrame`
    # use `TableView.switch_df` to set it
    df = None
    
    # i set/use them in `TableView.switch_df`
    # purely artificial artifact
    columns_to_hide = None
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( PandasTableModel, self ).__init__(
            parent, *args, **kwargs )
        
        self.df = pd.DataFrame()
        self.columns_to_hide = None

    def rowCount( self, parent=None ):
        # Reserved `PyQt5` method.
        return len( self.df.index )

    def columnCount( self, parent=None ):
        # Reserved `PyQt5` method.
        return self.df.columns.size

    def flags( self, index ):
        
        # Reserved `PyQt5` method.
        
        # This function was annotated with the aid of
        # an AI assistant.
        
        # I end up here whenever GUI (`view` or `delegate`)
        # needs to decide:
        # which actions are available for this specific
        # `table item` (cell)?
        # I can set custom behaviours: for example,
        # forbid editing all cells with `index` = something.
        
        # At this moment all items are movable, editable, etc.
        # Any changes should be made in subclasses.
        
        flags = super( PandasTableModel, self ).flags(index)
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def data( self, index, role=Qt.DisplayRole ):
        
        # Reserved `PyQt5` method. Is called when
        # GUI wants to show value in a table `cell`.
        
        if not index.isValid(): return

        if role == Qt.DisplayRole:
            # just showing
            value = self.df.iloc[ index.row(), index.column() ]
            return '' if pd.isna(value) else str(value)

    def setData( self, index, value, role=Qt.EditRole ):
        
        # Reserved `PyQt5` method. Is called when
        # I edit some cell in GUI and want to write changes
        # to the underlying array.
        
        if role==Qt.EditRole:
            self.df.iloc[ index.row(), index.column() ] = str(value)
            self.dataChanged.emit( index, index )
            return True

        return False

    def headerData( self, iloc,
        orientation=Qt.Horizontal, role=Qt.DisplayRole ):
                
        # Reserved `PyQt5` method. Is called when
        # GUI wants to show user-friendly text
        # in table header row.
        
        if orientation==Qt.Horizontal and role==Qt.DisplayRole:
            # table header, just showing
            if self.columnCount()==0: return 'NODATA'
            return self.df.columns[iloc]

        return None
        
    def sort( self, coliloc, sort_order ):
            
        # Reserved `PyQt5` method. Sorts underlying data however I want,
        # this affects GUI.
        
        # help:
        # https://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttablemodel/
        
        if coliloc >= self.columnCount(): return
        
        self.layoutAboutToBeChanged.emit()
        
        col = self.df.columns[ coliloc ]
        is_asc = True if sort_order==Qt.AscendingOrder else False
    
        # simple sorting
        #self.df.sort_values( col, inplace=True, ascending=is_asc )
        
        # natural sorting between numbers ans strings
        # help:
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
        self.df.sort_values(
            col, inplace=True, ascending=is_asc,
            key=lambda x: argsort( index_natsorted(self.df[col]) )
            )
            
        self.layoutChanged.emit()
    
    def supportedDragActions( self ):
        
        # The user `drags` something from here.
        # I allow to do specific `actions`.
    
        # This function was created with the aid of
        # an AI assistant.
        
        # help:
        # https://stackoverflow.com/questions/61387248/in-pyqt5-how-do-i-properly-move-rows-in-a-qtableview-using-dragdrop
        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QAbstractItemModel.html
        
        return Qt.MoveAction

    def supportedDropActions( self ):
        
        # The user brings here something.
        # I plan to do specific `actions`.
        
        return Qt.MoveAction | Qt.CopyAction
    
    def mimeTypes( self ):
        
        # Reserved `PyQt5` method.
        
        # This function was created/annotated with the aid of
        # an AI assistant.
        
        # Whenever I want to drag/drop something, I request
        # programs to `encode something into MIME data` or
        # `decode something from MIME data`.
        
        # This function allows my GUI to know it's
        # capabilities and limitations - which MIME data it
        # can process. This way whenever something inedible is
        # thrown into this GUI, GUI will reject it.
        
        # It is possible to define custom MIME types.
        # It is possible to find and use existing MIME types.
        # help:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        # https://www.iana.org/assignments/media-types/media-types.xhtml
        
        # use QMimeData.formats() to inspect dropEvents and
        # add necessary types here
        
        types = [
            EMimeTypes.TEXT_PLAIN,
            EMimeTypes.TEXT_URI_LIST,
            EMimeTypes.APPLICATION_QT_WINDOWS_MIME,
            ]
        types.extend( super( PandasTableModel, self ).mimeTypes() )
        return types
    
    def mimeData( self, indexes ):
        
        # Reserved `PyQt5` method.
        
        # This function was created/annotated with the aid of
        # an AI assistant.
        
        # I end up here whenever I want to export
        # something from this widget into clipboard / somewhere else.
        # `Something` = table cells that have given `indexes`.
        # `Clipboard` = MIME data.
        # `Somewhere else` = other widgets, other applications,
        # anything, that can process MIME data.
        
        # This is a standard way of communication between
        # apps and widgets.
        # Yet when I transfer items between my own widgets,
        # there is no need to encode and decode data.
        # For example, from `PandasTableView1` into `PandasTableView2`.
        
        # Currently the process is as follows (plan A):
        # 1) widget knows that I want to drag it's contents somewhere
        # 2) widget encodes selected data into MIME data
        # 3) widget has no care about anything else.
        # Alternative perspective (plan B):
        # 1) widget knows that I want to drag it's contents somewhere
        # 2) widget waits until it knows where exactly I intend to drag it's data
        # 3) widget decides whether to encode / give raw data to the destination.
        
        # Default PyQt5 methods work according to `plan A`.
        # Implementing `plan B` requires overriding default
        # `drag and drop` behaviors. This means that
        # 1) make sure `plan A` works
        # 2) maybe start thinking about `plan B`.
        
        # help:
        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QMimeData.html
        
        return super( PandasTableModel, self ).mimeData( indexes )
    
    def dropMimeData( self, data, action, row, column, parent_index ):
        
        # Reserved `PyQt5` method.
        
        # This function was created/annotated with the aid of
        # an AI assistant.
        
        # This function must return `True` or `False`,
        # depending on whether it accepted dropped data or not.
        
        # I end up here whenever this GUI widget receives `MIME data`.
        # In other words,
        # I end up here whenever this GUI widget receives
        # any kind of drops (because all drops = MIME data).
        
        # Function parameters:
        # `data` = MIME data I need to parse
        # `action` = one of the predefined `Qt.DropAction` types
        # `row`, `column` = on which cell this data was dropped
        # `parent` = parent `index` of cell with given `row` and `column`
        # (makes sense only when my underlying data is a tree. Currently
        # my underlying data is a table,
        # so parent should be = `invalid index`,
        # which means `root of the model`).
        
        # So, at this moment I know that
        # 1) some source widget has created a `drop event`
        # with specific `MIME data` and a certain proposed `drop action`
        # 2) this GUI widget has received this `drop event`,
        # checked `MIME data` type and `drop action` type,
        # made any corrections needed
        # 3) this GUI widget decided that it wants to
        # process given `MIME data` according to the corrected `drop event`.
            
        if action == Qt.IgnoreAction:
            # i chose to ignore this mime data,
            # tell everyone that i do not accept
            # although why would i end up here if it makes
            # more sense to reject the `drop event` in the
            # dedicated `drop event received` method?
            # why did this `drop event` get this far?
            return False
        
        elif action == Qt.MoveAction:
            
            # TODO
            # update pyqt5 to version 5.6 (at least)
            # bc i can't call data.mimeTypes()
            # to see a `list of str` with actual `EMimeTypes`
            # this `QMimeData` object named `data` carries
            
            # also i can't check that the `data` parent is self
            # too much ambiguity
            
            # i have some expected values
            if data.hasText():
                if data.text() == '':
                    
                    subdf_index = data.property( ColumnsMimeText.drag_df_locs )
                    if not subdf_index is None:
                        # communicate back to `view`
                        rowilocs = list(range( row, row+len(subdf_index) ))
                        data.setProperty( ColumnsMimeText.set_selected_rowilocs, rowilocs )
                        # perform actions
                        return self.__reorder_subdf( subdf_index, row )
        
        log.error( 'not implemented, rejecting by default' )
        return False
    
    def add_column( self, column, values ):
            
        # My custom method. I may use it manually.
        
        self.layoutAboutToBeChanged.emit()
        
        if type( values ) == list:
            
            if not len(values)==self.rowCount():
                raise IndexError
                
            self.df[column] = values
            
        else:
            self.df[column] = str(values)

        self.layoutChanged.emit()
        
    def add_rows( self, rows ):
            
        # My custom method. I may use it manually.
        # I convert these `rows` to `df`. This `df` lacks predictable
        # `df.index`.
        # TODO
        # allow to specify index / subclasses need
        # to explicitly allow this method in order to avoid
        # unpredictable `df.index` values

        self.layoutAboutToBeChanged.emit()

        df = pd.DataFrame( rows )
        self.df = self.df.append( df, ignore_index=True )

        self.layoutChanged.emit()

    def add_df( self, df ):
            
        # My custom method. I may use it manually.
        # Assumes that `df.index` is in harmony with `self.df.index`.

        self.layoutAboutToBeChanged.emit()

        self.df = self.df.append( df )

        self.layoutChanged.emit()

    def delete_rows( self, rowilocs ):
            
        # My custom method. I may use it manually.

        if self.rowCount()==0: return
        
        self.layoutAboutToBeChanged.emit()

        index = self.df.iloc[ rowilocs ].index
        self.df.drop( index=index, inplace=True )
        
        if self.rowCount()==0:
            # reset columns as well
            self.df = pd.DataFrame()
        
        self.layoutChanged.emit()
        
    def switch_df( self, df ):
            
        # My custom method. I may use it manually.
        # Completely replaces underlying `df`, GUI table headers.

        self.layoutAboutToBeChanged.emit()
        self.df = df
        self.layoutChanged.emit()
            
    def replace_row_series( self, new_s ):
            
        # My custom method. I may use it manually.
        # Completely replaces specific `self.df` rows
        # with matching `new_s.index`.
        
        self.layoutAboutToBeChanged.emit()
        
        same_index = self.df.index.isin( new_s.index )
        self.df.loc[ same_index, new_s.name ] = new_s.values
        
        self.layoutChanged.emit()

    def replace_subdf( self, df ):
            
        # My custom method. I may use it manually.
        # Replaces specific `self.df` items that match specific `df` items
        # (according to `df.index`),
        # this affects GUI.
        
        if len(df)==0: return
        
        self.layoutAboutToBeChanged.emit()
            
        # delete old, insert new
        for col in self.df.columns:
            self.df.loc[ df.index, col ] = pd.NA
        for col in df.columns:
            self.df.loc[ df.index, col ] = df[col]
        
        # remove only fully empty rows
        self.df.dropna( how='all', inplace=True )
        
        self.layoutChanged.emit()
                
    def __reorder_subdf( self, subdf_index, target_rowiloc ):
        
        # My custom method. I may use it manually.
        
        # I want to reposition rows with given
        # `subdf_index`.
        # How it was:
        # ----x---x-xxxx--x
        # How i want it to be:
        # --xxxxxxx--------
        # Because i moved my mouse here:
        # --!--------------
        
        # foolcheck
        if subdf_index is None:
            return False
        elif not subdf_index.isin( self.df.index ).all():
            log.error( 'given subdf index does not describe items from self.df - these are two different indexes, not doing anything' )
            return False
        elif not type( subdf_index ) is pd.Int64Index:
            log.error( 'unknown index format, need pd.Int64Index, not implemented, not doing anything' )
            return False
            
        # obtain old index excluding `subdf_index`
        old_index = list(self.df.index[ ~self.df.index.isin(subdf_index) ])
        
        # some rows retain their positions
        new_index = old_index[:target_rowiloc]
        
        # then i need to group the `subdf` ones
        new_index.extend( list(subdf_index) )
        
        # then i need to add the rest of them
        # while retaining their order
        for v in old_index[target_rowiloc:]:
            if not v in new_index:
                new_index.append( v )
        
        # apply the new index to sort rows
        self.layoutAboutToBeChanged.emit()
        self.df = self.df.reindex([ loc for loc in new_index ])
        self.layoutChanged.emit()
        
        return True
    
#---------------------------------------------------------------------------+++
# end 2023.10.20
# __reorder_subdf

