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
    
    # Universal widget for viewing a single `pd.DataFrame`
    # full of strings.

    _MODEL = None
    
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
        self._MODEL = PandasTableModel( self )
        self.setModel( self._MODEL )

    def rowCount( self, parent=None ):
        return self._MODEL.rowCount()

    def columnCount( self, parent=None ):
        return self._MODEL.columnCount()
    
    def selectedItems( self ):

        # help:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview

        sel = self.selectionModel()

        if not sel.hasSelection(): return []
        return sel.selectedRows()
      
    def selected_rowilocs( self ):
        
        # Allows me to get the exact row numbers
        # that are currently selected.

        rowilocs = []
        for item in self.selectedItems():
            rowiloc = item.row()
            rowilocs.append( rowiloc )
            
        return list( set(rowilocs) )
            
    def selected_subdf( self ):
        
        # Allows me to get a valid `pd.DataFrame`
        # with currently selected items.
        
        if self._MODEL.rowCount()==0:
            return pd.DataFrame()
        
        rowilocs = self.selected_rowilocs()
        return self._MODEL.df.iloc[rowilocs]
    
    def select_next_row( self, rowiloc, after=True ):
        
        # Allows me to safely select a single row.
        
        last_row = self._MODEL.rowCount()-1
        next_row = 0 if after else 1
        if last_row>next_row:
            # selecting next row is possible
            if rowiloc>last_row:
                # current row is already the last one
                self.selectRow( last_row if after else last_row-1 )
            else:
                self.selectRow( rowiloc )

        # its impossible to select next row
        # as it does not exist
    
    def delete_rows( self, rowilocs ):

        if len(rowilocs)==0: return
        
        self._MODEL.delete_rows( rowilocs )
        
    def delete_selection( self ):
        
        rowilocs = self.selected_rowilocs()
        if len(rowilocs)==0: return

        self._MODEL.delete_rows( rowilocs )

        self.select_next_row( rowilocs[0] )
        
    def get_df( self ):
        # For external use only.
        return self._MODEL.df

    def switch_df( self, df, columns_to_hide=None ):
        
        # Completely changes current data.
        
        self._MODEL.switch_df( df, columns_to_hide=columns_to_hide )
        self._force_font_metrics()

        # set hidden columns
        
        if self._MODEL.columns_to_hide is None:
            return
        
        for coliloc, col in enumerate( self._MODEL.df.columns ):
            hide = col in self._MODEL.columns_to_hide
            hidden = self.isColumnHidden(coliloc)
            if hide and not hidden:
                self.setColumnHidden( coliloc, True )
            elif not hide and hidden:
                self.setColumnHidden( coliloc, False )
                
    def replace_row_series( self, new_s ):
        
        # Selectively replaces specific df row values.
        
        self._MODEL.replace_row_series( new_s )
        self._force_font_metrics()
    
    def replace_subdf( self, df ):
        self._MODEL.replace_subdf( df )
        self._force_font_metrics()
            
    def add_rows( self, rows ):
        
        # Just adds new rows ignoring the index.
        
        self._MODEL.add_rows( rows )
        self._force_font_metrics()
            
    def add_column( self, column, values ):
        self._MODEL.add_column( column, values )
        self._force_font_metrics()
            
    def add_df( self, df ):
        self._MODEL.add_df( df )
        self._force_font_metrics()
            
    def _force_font_metrics( self ):
               
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self._MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
        
#---------------------------------------------------------------------------+++
# end 2023.10.03
# allowed descendants to access `model`
# hidden columns ok
