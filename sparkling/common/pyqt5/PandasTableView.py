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
from PyQt5.QtCore import Qt, QMimeData, QItemSelectionModel, QItemSelection
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtGui import QDrag
# same project
from sparkling.common.pyqt5.PandasTableModel import (
    PandasTableModel,
    BaseColumns, ColumnsMimeText
    )
#from sparkling.common.enums.MimeTypes import EMimeTypes
        
class EMouseMoveModes( BaseColumns ):
    
    # the default behavior - when don't know that to do, do this
    drag_select = 0
    
    # i explicitly indicate that i just stopped
    # doing `drag_select`
    #drag_select_finished = 
    
    # alternative operation - what to do when i move
    # already selected items
    drag_move_selection = 1

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
        self.setDragDropMode( QAbstractItemView.DragDrop )

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
    
    def dragEnterEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # I can filter out unsupported events
        # the moment they are dragged into this widget.

        if ev.source() is self:
            # i sent this event
            ev.accept()
            return

        log.error( 'not implemented yet' )
        ev.ignore()
        
    def dropEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # This function was created with the aid of
        # an AI assistant.
        
        # need to override because
        # it gives incorrect `row` and `column`
        # to `self._MODEL.dropMimeData`
        
        ev.accept()
        
        # request model to do something
        pos = ev.pos()
        rowiloc = self.rowAt(pos.y())
        coliloc = self.columnAt(pos.x())
        success = self._MODEL.dropMimeData( ev.mimeData(), ev.dropAction(), rowiloc, coliloc, self.rootIndex() )
        
        if not success:
            return
        
        # model may request view to do something
        # via `mimeData properties`
        
        # change selection
        selection_rowilocs = ev.mimeData().property( ColumnsMimeText.set_selected_rowilocs )
        if type(selection_rowilocs) is list:
            self.clearSelection()
            if len(selection_rowilocs) > 0:
                # currently i can only select 1 block of rows
                # TODO
                # select precisely selection_rowilocs in a sane way
                
                # i received specific rowilocs
                # i may need to appropriate them in they
                # exceed number of existing items
                
                n_rows = self.rowCount()
                n_overflow = len(selection_rowilocs)
                
                # of the first element in block
                target_rowiloc = selection_rowilocs[0]
                
                # make sure i can select these items
                if target_rowiloc + n_overflow > n_rows:
                    # move all block rowilocs up
                    # until they fit
                    target_rowiloc = n_rows - n_overflow
                    if target_rowiloc < 0: target_rowiloc = 0
                    new_selection = QItemSelection(
                        self._MODEL.index( target_rowiloc, coliloc ),
                        self._MODEL.index( n_rows-1, coliloc )
                        )
                    self.selectionModel().select( new_selection, QItemSelectionModel.Select|QItemSelectionModel.Rows )
                    return
                
                # i can safely select items
                new_selection = QItemSelection(
                    self._MODEL.index( target_rowiloc, coliloc ),
                    self._MODEL.index( target_rowiloc+n_overflow-1, coliloc )
                    )
                self.selectionModel().select( new_selection, QItemSelectionModel.Select|QItemSelectionModel.Rows )
    
    #def dragMoveEvent( self, ev ):
    #    print( 'dragMoveEvent' )
    
    #def dragLeaveEvent( self, ev ):
    #    print( 'dragLeaveEvent' )
        
    def mousePressEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # i want to know current situation before
        # processing this mouse click
        
        #print( 'mousePressEvent start', self.__mouse_move_mode )
        
        if ev.buttons() & Qt.LeftButton:
            # at this moment i started holding the
            # left mouse button
            
            # is the thing under the mouse already selected?
            if self.selectionModel().hasSelection():
                # i have selected something, where is it?
                
                # which item is currently under the mouse pointer?
                index = self.indexAt( ev.pos() )
                if index.isValid():
                    # it is possible to further inspect this item
                    
                    if self.selectionModel().isSelected(index):
                        # i want to move all currently selected items
                        self.__mouse_move_mode = EMouseMoveModes.drag_move_selection
                    else:
                        # i want to start selecting items from scratch
                        # regardless of any previous intentions
                        self.__mouse_move_mode = EMouseMoveModes.drag_select
                else:
                    # idk what is this, go back to default mode
                    self.__mouse_move_mode = EMouseMoveModes.drag_select
            
            else:
                # nothing is selected, which means that
                # i want to start selecting multiple items
                # while dragging the mouse
                self.__mouse_move_mode = EMouseMoveModes.drag_select
        
        # proceed
        super( PandasTableView, self ).mousePressEvent( ev )
    
        #print( 'mousePressEvent end  ', self.__mouse_move_mode )
        
    def mouseMoveEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # i want precise and predictable behavior,
        # so i don't call `super`
        
        # i want to override the creation of `QDrag`
        
        if ev.buttons() & Qt.LeftButton:
            # at this moment i am holding something
            # and started/continuing to move the mouse
            
            if self.__mouse_move_mode == EMouseMoveModes.drag_select:
                # i want to continue selecting items
                # while the user moves the mouse
                
                # which item is currently under the mouse pointer?
                # help:
                # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QAbstractItemView.html#PySide2.QtWidgets.PySide2.QtWidgets.QAbstractItemView.indexAt
                index = self.indexAt( ev.pos() )
                if index.isValid():
                    # it is possible to add this item to current selection
                    # this section was created with the aid of
                    # an AI assistant
                    # help:
                    # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QItemSelectionModel.html
                    if not self.selectionModel().isSelected(index):
                        self.selectionModel().select( index, QItemSelectionModel.Select|QItemSelectionModel.Rows )
        
            elif self.__mouse_move_mode == EMouseMoveModes.drag_move_selection:
                # i want to reposition selected items
                # this section was created with the aid of
                # an AI assistant
                
                # just in case
                if self.selectionModel().hasSelection():
                    # create very customized drag event
                    
                    # `self` is parent widget (event sender)
                    DragEv = QDrag( self )
                    
                    # encode selected `df` `locs`
                    mime_data = QMimeData()
                    #subdf_index = ' '.join( self.selected_subdf().index.astype(str) )
                    subdf_index = self.selected_subdf().index
                    #mime_data.setText( ColumnsMimeText.encode_into_text({
                    #    ColumnsMimeText.drag_df_locs: subdf_index )
                    #    }) )
                    mime_data.setText( '' ) # it assigns `EMimeTypes.TEXT_PLAIN`
                    mime_data.setProperty( ColumnsMimeText.drag_df_locs, subdf_index )
                    
                    DragEv.setMimeData( mime_data )
                    
                    # some kind of image
                    #DragEv.setPixmap()
                    # where to show mouse cursor relative to image
                    #DragEv.setHotSpot()
                    
                    # start drag/dropping
                    # time gets paused, so my current `ev.pos`
                    # becomes obsolete - i may have moved mouse
                    # anywhere
                    performed_action = DragEv.exec_( Qt.MoveAction )
                    # if performed_action == Qt.MoveAction:
                    #     # this event was accepted - `self._MODEL`
                    #     # reordered necessary rows,
                    #     # yet the items selected in view remain the same
                    #     # i need to manually reapply selection
                    #     # but in this method i can't easily get up-to-date
                    #     # ev.pos(), so i process everything in
                    #     # self.dropEvent
                        
                else:
                    log.debug( 'why am i here?' )
    
    """
    def mouseReleaseEvent( self, ev ):

        # Reserved `PyQt5` method.
        
        # i want to know current situation before
        # processing this mouse click
        
        print( 'mouseReleaseEvent start', self.__mouse_move_mode )
        
        if self.__mouse_move_mode==EMouseMoveModes.drag_select:
            # explicitly indicate that i stopped
            # selecting
            self.__mouse_move_mode = EMouseMoveModes.drag_select_finished
        
        print( 'mouseReleaseEvent end  ', self.__mouse_move_mode )
    """
        
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
