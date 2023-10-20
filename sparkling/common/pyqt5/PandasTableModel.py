# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom `QAbstractTableModel` that works well
# with `pandas.DataFrame`.

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
        
        return super( PandasTableModel, self ).mimeTypes()
    
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
    
    def dropMimeData( self, data, action, row, column, parent ):
        
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
                
#---------------------------------------------------------------------------+++
# end 2023.10.20
# better comments

