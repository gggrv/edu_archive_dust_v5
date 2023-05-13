# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom pandas table model.

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
    
    df = None
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( PandasTableModel, self ).__init__(
            parent, *args, **kwargs )
        
        self.df = pd.DataFrame()

    def rowCount( self, parent=None ):
        return len( self.df.index )

    def columnCount( self, parent=None ):
        return self.df.columns.size

    def flags( self, index ):
        flags = super( self.__class__, self ).flags(index)
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags

    def data( self, index, role=Qt.DisplayRole ):
        if not index.isValid(): return

        if role == Qt.DisplayRole:
            value = self.df.iloc[ index.row(), index.column() ]
            return '' if pd.isna(value) else str(value)

    def setData( self, index, value, role=Qt.EditRole ):
        
        if role==Qt.EditRole:
            self.df.iloc[ index.row(), index.column() ] = str(value)
            self.dataChanged.emit( index, index )
            return True

        return False

    def headerData( self, iloc,
            orientation=Qt.Horizontal, role=Qt.DisplayRole ):
        
        if orientation==Qt.Horizontal and role==Qt.DisplayRole:
            if self.columnCount()==0: return 'NODATA'
            return self.df.columns[iloc]

        return None
    
    def add_column( self, column, values ):
        
        if type( values ) == list:
            
            if not len(values)==self.rowCount():
                raise IndexError
                
            self.df[column] = values
            
        else:
            self.df[column] = str(values)

    def add_rows( self, rows ):

        self.layoutAboutToBeChanged.emit()

        df = pd.DataFrame( rows )
        self.df = self.df.append( df, ignore_index=True )

        self.layoutChanged.emit()

    def add_df( self, df ):

        self.layoutAboutToBeChanged.emit()

        self.df = self.df.append( df )

        self.layoutChanged.emit()

    def delete_rows( self, rowilocs ):

        if self.rowCount()==0: return
        
        self.layoutAboutToBeChanged.emit()

        index = self.df.iloc[ rowilocs ].index
        self.df.drop( index=index, inplace=True )
        
        if self.rowCount()==0:
            # reset columns as well
            self.df = pd.DataFrame()
        
        self.layoutChanged.emit()
        
    def switch_df( self, df ):

        self.layoutAboutToBeChanged.emit()
        self.df = df
        self.layoutChanged.emit()
        
    def sort( self, coliloc, sort_order ):
        
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

    def replace_subdf( self, df ):
        
        # Replaces self.df items with same index as in df,
        # updates view layout.
        
        if len(df)==0: return
        
        self.layoutAboutToBeChanged.emit()
            
        # delete old, insert new
        for col in self.df.columns:
            self.df.loc[ df.index, col ] = pd.NA
        for col in df.columns:
            self.df.loc[ df.index, col ] = df[col]
        
        # remove empty
        self.df.dropna( how='all', inplace=True )
        
        self.layoutChanged.emit()
                
#---------------------------------------------------------------------------+++
# end 2023.01.10
# cleaned
