# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom pandas table view.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
from PyQt5.QtWidgets import QTableView
# same project
from sparkling.common.pyqt5.PandasTableModel import PandasTableModel
        
# Basic table view that works efficiently with
# pandas DataFrames. Has some default .css settings.
class PandasTableView( QTableView ):

    __MODEL = None

    def __init__( self,
                  parent,
                  *args, **kwargs ):
        super( PandasTableView, self ).__init__( parent, *args, **kwargs )

        # appearance
        self.setShowGrid( False )
        self.setAlternatingRowColors( True )
        self.setSelectionBehavior( self.SelectRows )
        self.setWordWrap( False )
        self.setSortingEnabled( True )

        # instantly populate
        self.__MODEL = PandasTableModel( self )
        self.setModel( self.__MODEL )

    def rowCount( self, parent=None ):
        return self.__MODEL.rowCount()

    def columnCount( self, parent=None ):
        return self.__MODEL.columnCount()
    
    def selectedItems( self ):

        # help:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview

        sel = self.selectionModel()

        if not sel.hasSelection(): return []
        return sel.selectedRows()
      
    def selectedRowilocs( self ):

        rowilocs = []
        for item in self.selectedItems():
            rowiloc = item.row()
            rowilocs.append( rowiloc )
            
        return list( set(rowilocs) )
            
    def selectedSubdf( self ):
        
        if self.__MODEL.rowCount()==0:
            return pd.DataFrame()
        
        rowilocs = self.selectedRowilocs()
        return self.__MODEL.df.iloc[rowilocs]
    
    def select_next_row( self, rowiloc, after=True ):
        
        last_row = self.__MODEL.rowCount()-1
        next_row = 0 if after else 1
        if last_row>next_row:
            # selecting next row is possible
            if rowiloc>last_row:
                # current row is already last one
                self.selectRow( last_row if after else last_row-1 )
            else:
                self.selectRow( rowiloc )

        # its impossible to select next row
        # as it does not exist
    
    def delete_rows( self, rowilocs ):

        if len(rowilocs)==0: return
        
        self.__MODEL.delete_rows( rowilocs )
        
    def delete_selection( self ):
        
        rowilocs = self.selectedRowilocs()
        if len(rowilocs)==0: return

        self.__MODEL.delete_rows( rowilocs )

        self.select_next_row( rowilocs[0] )
        
    def get_df( self ):
        return self.__MODEL.df
        
    def get_df_index( self ):
        return self.__MODEL.df.index
        
    def get_df_columns( self ):
        return self.__MODEL.df.columns

    def switch_df( self, df, hidden_colilocs=None ):
        
        # Completely changes current data.
        
        self.__MODEL.switch_df(df)
        
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )

        # set hidden columns
        if hidden_colilocs is not None:
            for coliloc in hidden_colilocs:
                self.setColumnHidden(coliloc,True)
                
    def replace_values( self, new_s ):
        
        # Replaces some df values.
        
        self.__MODEL.replace_values( new_s )
                
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
    
    def replace_subdf( self, df ):
        
        self.__MODEL.replace_subdf( df )
                
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
            
    def add_rows( self, rows ):
        
        # Just adds new rows ignoring the index.
        
        self.__MODEL.add_rows( rows )
        
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
            
    def add_column( self, column, values ):
        
        self.__MODEL.add_column( column, values )

        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
            
    def add_df( self, df ):
        
        self.__MODEL.add_df( df )
        
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self.__MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
            
    def _custom_add_begin( self ):
        # For subclasses only.
        self.__MODEL.layoutAboutToBeChanged.emit()
    def _custom_add_end( self ):
        # For subclasses only.
        self.__MODEL.layoutChanged.emit()
        
#---------------------------------------------------------------------------+++
# end 2023.05.12
# removed unused and unstable functions
