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
        flags = super( self.__class__, self ).flags(index)
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

