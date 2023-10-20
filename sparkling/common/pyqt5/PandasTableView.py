# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom `QTableView` that works well
# with `PandasTableModel`.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
# same project
from sparkling.common.pyqt5.PandasTableModel import PandasTableModel
from sparkling.common.BaseColumns import BaseColumns
        
class EMouseMoveModes( BaseColumns ):
    
    # the default behavior - when don't know that to do, do this
    drag_select = 0

class PandasTableView( QTableView ):

    # Universal widget for viewing a single `pd.DataFrame`
    # full of strings.
    # Has some default .css settings.
    
    # At this moment selecting an item and dragging it with mouse
    # will result in multiple item selection.

    _MODEL = None
    
    # the user may press a button and drag a mouse across
    # this widget, widget reactions may vary
    __mouse_move_mode = EMouseMoveModes.drag_select
    
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
        # Reserved `PyQt5` method.
        return self._MODEL.rowCount()

    def columnCount( self, parent=None ):
        # Reserved `PyQt5` method.
        return self._MODEL.columnCount()
    
    def selectedItems( self ):

        # Reserved `PyQt5` method. Returns some internal
        # `PyQt5` items.
        
        # help:
        # https://stackoverflow.com/questions/5927499/how-to-get-selected-rows-in-qtableview

        sel = self.selectionModel()

        if not sel.hasSelection(): return []
        return sel.selectedRows()
    
    def mousePressEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # i want to know current situation before
        # processing this mouse click
        
        if ev.buttons() & Qt.LeftButton:
            # at this moment i started holding the
            # left mouse button
            
            # is the thing under the mouse already selected?
            if self.selectionModel().hasSelection():
                pass
            else:
                # nothing is selected, which means that
                # i want to start selecting multiple items
                # while dragging the mouse
                self.__mouse_move_mode = EMouseMoveModes.drag_select
        
        # proceed
        super( PandasTableView, self ).mousePressEvent( ev )
    
    def mouseMoveEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # i want to override the creation of `QDrag`
        
        if ev.buttons() & Qt.LeftButton:
            # at this moment i am holding something
            # and started moving the mouse
            
            if self.__mouse_move_mode == EMouseMoveModes.drag_select:
                # i want to continue selecting items
                # while the user moves the mouse
                
                # which item is currently under the mouse pointer?
                # help:
                # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QAbstractItemView.html#PySide2.QtWidgets.PySide2.QtWidgets.QAbstractItemView.indexAt
                index = self.indexAt( ev.pos() )
                if index.isValid():
                    # i can select this item
                    
                    # so at this moment
                    # current implementation allows me
                    # to continuously change current selected row
                    # whlie the user moves the mouse
                    self.selectRow( index.row() )
      
    def selected_rowilocs( self ):
        
        # My custom method. I may use it manually.
        # Allows me to get the exact row numbers
        # that are currently selected.

        rowilocs = []
        for item in self.selectedItems():
            rowiloc = item.row()
            rowilocs.append( rowiloc )
            
        return list( set(rowilocs) )
            
    def selected_subdf( self ):
        
        # My custom method. I may use it manually.
        # Allows me to get a valid `pd.DataFrame`
        # with currently selected items.
        
        if self._MODEL.rowCount()==0:
            return pd.DataFrame()
        
        rowilocs = self.selected_rowilocs()
        return self._MODEL.df.iloc[rowilocs]
    
    def select_next_row( self, rowiloc, after=True ):
        
        # My custom method. I may use it manually.
        # Allows me to safely select a single row
        # that comes before/after given `rowiloc`.
        
        # I end up here only when I manually delete selection
        # from view.
        # This means that I either select given `rowiloc`,
        # or select `rowiloc-1`. Function title is misleading.
        
        # TODO
        # appropriate for other uses as well
        
        # in `self.df` i may have an unknown number of rows
        # in order to be able to `select a row after given rowiloc`,
        # i need so many rows
        minimum_number_of_rows = 0 if after else 1 # need to step back
        
        last_rowiloc = self._MODEL.rowCount()-1
        if last_rowiloc>minimum_number_of_rows:
            # selecting next row is possible
            if rowiloc > last_rowiloc:
                # i gave specific `rowiloc`, but it
                # exceeds the number of available rows,
                # so i want to select the last available one
                self.selectRow( last_rowiloc if after else last_rowiloc-1 )
            else:
                self.selectRow( rowiloc )

        # it is impossible to select next row
        # as it does not exist
    
    def delete_rows( self, rowilocs ):
        # My custom method. I may use it manually.
        if len(rowilocs)==0: return
        self._MODEL.delete_rows( rowilocs )
        
    def delete_selection( self ):
        
        # My custom method. I may use it manually.
        
        rowilocs = self.selected_rowilocs()
        if len(rowilocs)==0: return

        self._MODEL.delete_rows( rowilocs )

        self.select_next_row( rowilocs[0] )
        
    def get_df( self ):
        # My custom method. I may use it manually.
        # For external use only. I don't want anyone except
        # subclasses / special cases to access `self._variables`.
        return self._MODEL.df
    
    def reapply_columns_to_hide( self, columns_to_hide=None, appropriate_reverse=False ):
        
        # My custom method. I may use it manually.
        # Either I want to hide given columns, or to
        # show only given columns.
        
        # make sure i have `cols to hide`, not `cols to show`.
        if appropriate_reverse:
            # i have `cols to show`, need to reverse them;
            # `self._MODEL.columns_to_hide` must contain
            # `cols to hide` at all times, so i don't want to set
            # `columns_to_hide` = `self._MODEL.columns_to_hide`
            # if `columns_to_hide` is None
            
            # tell to hide all
            cols_to_hide = list( self._MODEL.df.columns )
            
            # also tell to unhide specific
            for col in columns_to_hide: # may cause error
                if col in cols_to_hide:
                    cols_to_hide.remove( col )
                    
            # assign correct variable value
            columns_to_hide = cols_to_hide
            
        # proceed
    
        # make sure i actually want to hide something
        self._MODEL.columns_to_hide = columns_to_hide
        if self._MODEL.columns_to_hide is None:
            return
        
        for coliloc, col in enumerate( self._MODEL.df.columns ):
            hide = col in self._MODEL.columns_to_hide
            hidden = self.isColumnHidden(coliloc)
            if hide and not hidden:
                self.setColumnHidden( coliloc, True )
            elif not hide and hidden:
                self.setColumnHidden( coliloc, False )

    def switch_df( self, df, columns_to_hide=None, appropriate_reverse=False ):
        
        # My custom method. I may use it manually.
        # Completely changes current data.
        
        self._MODEL.switch_df( df )
        self._force_font_metrics()

        self.reapply_columns_to_hide( columns_to_hide=columns_to_hide, appropriate_reverse=appropriate_reverse )
                
    def replace_row_series( self, new_s ):
        
        # My custom method. I may use it manually.
        # Selectively replaces specific df row values
        # based on `new_s.index`.
        
        self._MODEL.replace_row_series( new_s )
        self._force_font_metrics()
    
    def replace_subdf( self, df ):
        # My custom method. I may use it manually.
        self._MODEL.replace_subdf( df )
        self._force_font_metrics()
            
    def add_rows( self, rows ):
    
        # My custom method. I may use it manually.    
        # Just adds new rows ignoring the index.
        
        self._MODEL.add_rows( rows )
        self._force_font_metrics()
            
    def add_column( self, column, values ):
        # My custom method. I may use it manually.
        self._MODEL.add_column( column, values )
        self._force_font_metrics()
            
    def add_df( self, df ):
        # My custom method. I may use it manually.
        self._MODEL.add_df( df )
        self._force_font_metrics()
            
    def _force_font_metrics( self ):
               
        # My custom method. I may use it manually.
        
        # make sure rows have appropriate height
        font_height = self.fontMetrics().height()
        for rowiloc in range( self._MODEL.rowCount() ):
            self.setRowHeight( rowiloc, font_height )
        
#---------------------------------------------------------------------------+++
# end 2023.10.20
# better comments
