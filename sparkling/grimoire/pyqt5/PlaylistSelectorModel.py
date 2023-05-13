# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import ( Qt, QAbstractTableModel )
# same project
from sparkling.grimoire.Playlist import Columns

class PlaylistSelectorModel( QAbstractTableModel ):
    
    # future PlaylistManager
    # i expect it to be fully initialized
    mgr = None
    
    # the followinf two structures must match
    # these will be displayed for humans
    column_labels = [
        'Basename',
        'Name',
        'Order',
        'Database'
        ]
    # these will be used for metadata updating
    column_keys = [
        None,
        Columns.SCREEN_NAME,
        Columns.ORDER,
        Columns.DB_NAME
        ]
    
    def __init__( self,
                  playlist_manager,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistSelectorModel, self ).__init__(
            parent, *args, **kwargs )
        
        self.mgr = playlist_manager

    def rowCount( self, parent=None ):
        return len( self.mgr._playlists )

    def columnCount( self, parent=None ):
        return 4

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

        if role == Qt.DisplayRole or role == Qt.EditRole:
            
            # get playlist
            p = self.mgr._playlists[ index.row() ]
            
            # get value
            coliloc = index.column()
            if coliloc==0:
                return p.basename()
            if coliloc==1:
                return p.screen_name()
            if coliloc==2:
                return p.order()
            if coliloc==3:
                # this text is hidden behind
                # custom cell widget
                # that i add in dedicated view class
                return p.db_name()

    def setData( self, index, value, role=Qt.EditRole ):
        
        value = str(value)
        
        if role==Qt.EditRole:
            
            # get playlist
            p = self.mgr._playlists[ index.row() ]
            
            # set value
            coliloc = index.column()
            if coliloc==0:
                p.set_basename( value )
            if coliloc==1:
                p.set_screen_name( value )
            if coliloc==2:
                p.set_order( value )
            if coliloc==3:
                p.set_db_name( value )
            
            self.dataChanged.emit( index, index )
            return True

        return False

    def headerData( self, iloc,
            orientation=Qt.Horizontal, role=Qt.DisplayRole ):
        
        if orientation==Qt.Horizontal and role==Qt.DisplayRole:
            if self.columnCount()==0: return 'NODATA'
            return PlaylistSelectorModel.column_labels[iloc]

        return None

    def add_playlists( self, how_many ):

        self.layoutAboutToBeChanged.emit()

        for _ in range( how_many ):
            self.mgr.new_playlist()

        self.layoutChanged.emit()

    def delete_playlists( self, rowilocs_or_basenames ):

        if self.rowCount()==0: return
        
        self.layoutAboutToBeChanged.emit()
        
        basenames = []
        for v in rowilocs_or_basenames:
            if type(v)==int:
                p = self.mgr._playlists[v]
                basenames.append( p.basename() )
            else:
                basenames.append( v )
                
        self.mgr.delete_playlists( basenames )
        
        self.layoutChanged.emit()
        
    def switch_playlist_manager( self, playlist_manager ):

        self.layoutAboutToBeChanged.emit()
        self.mgr = playlist_manager
        self.layoutChanged.emit()
        
    def current_global_active_playlist( self ):
        
        # Returns THE playlist that is
        # considered to be currently active globally -
        # across the whole application scope.
        # Only one playlist can be *active* at a time,
        # even though many playlists can be *open* at the same time.
        
        return self.mgr.current_active_playlist()
                
#---------------------------------------------------------------------------+++
# end 2023.05.13
# global active playlist
