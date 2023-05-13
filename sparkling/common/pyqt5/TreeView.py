# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtWidgets import QTreeView
# same project

class TreeView( QTreeView ):

    _MODEL = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( TreeView, self ).__init__( parent, *args, **kwargs )

        self.setAlternatingRowColors( True )
        self.setSelectionBehavior( self.SelectRows )
        self.setWordWrap( False )
        self.setUniformRowHeights( True )
        self.setHeaderHidden( True )
        
    def switch_model( self, model ):
        
        self.setModel( model )
        self._MODEL = model
        
    def switch_root_node( self, root_node, hidden_colilocs=None ):

        self._MODEL.switch_root_node( root_node )

        # set hidden columns
        if hidden_colilocs:
            for coliloc in hidden_colilocs:
                self.setColumnHidden(coliloc,True)
                
    def selected_nodes( self ):
        
        # Returns list of selected nodes.
        
        # help:
        # https://stackoverflow.com/questions/29680105/how-to-get-the-pyqt-qtreeview-item-child-using-double-click-event
        
        selected_nodes = []
        for index in self.selectedIndexes():
            selected_nodes.append( index.internalPointer() )
        return selected_nodes
    
    def clear( self ):
        del self._MODEL.root_node
                
#---------------------------------------------------------------------------+++
# end 2023.03.08
# renamed
