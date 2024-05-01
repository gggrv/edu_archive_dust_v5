# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import pandas as pd
# pip install
from PyQt5.QtCore import ( Qt, QAbstractItemModel, QModelIndex )
# same project
from sparkling.common.TreeNode import TreeNode

class TreeModel( QAbstractItemModel ):
    
    # help:
    # https://gist.github.com/danieljfarrell/6e94aa6f8c3c437d901fd15b7b931afb
    
    root_node = None # will become TreeNode
    header_labels = None
    
    def __init__( self,
                  parent=None,
                  root_node=None,
                  *args, **kwargs ):
        super( TreeModel, self ).__init__( parent, *args, **kwargs )
        
        # sample empty node, can be overwritten later
        self.root_node = root_node if root_node else TreeNode()
        
    def parent( self, index ):
        
        # Returns parent node of node with given index.
        
        if self.root_node is None:
            return QModelIndex()
        
        if index.isValid():
            node = index.internalPointer()
            if node.parent_node:
                subnodeiloc = node.parent_node.get_subnodeiloc( node )
                return QAbstractItemModel.createIndex(
                    self,
                    subnodeiloc,
                    0,
                    node.parent_node
                    )
        
        return QModelIndex()
        
    def index( self, rowiloc, coliloc, parent_index=None ):
        
        if self.root_node is None:
            return QModelIndex()
        
        # obtain parent node
        parent_node = None
        if not parent_index or not parent_index.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent_index.internalPointer()

        if not QAbstractItemModel.hasIndex(
                self, rowiloc, coliloc, parent_index ):
            return QModelIndex()

        if rowiloc < len( parent_node.subnodes ):
            node = parent_node.subnodes[rowiloc]
            return QAbstractItemModel.createIndex(
                self, rowiloc, coliloc, node )
        else:
            return QModelIndex()

    def rowCount( self, index ):
        
        if self.root_node is None:
            return 0
        
        if index.isValid():
            return len( index.internalPointer().subnodes )
        return len( self.root_node.subnodes )

    def columnCount( self, index ):
        
        if self.root_node is None:
            return 0
        
        ncols = len( self.root_node.values )
        if ncols>0: return ncols
        
        if len( self.root_node.subnodes )>0:
            return 1
        
        return 0

    def data( self, index, role=Qt.DisplayRole ):
        if not index.isValid(): return
        
        rowiloc, coliloc = index.row(), index.column()
        node = index.internalPointer()

        if role == Qt.DisplayRole:
            value = node.values[coliloc]
            is_none = ( value is None ) or pd.isna(value).all()
            return '' if is_none else str(value)
        
    def switch_root_node( self, root_node ):
            
        self.layoutAboutToBeChanged.emit()
        self.root_node = root_node
        self.layoutChanged.emit()
                
#---------------------------------------------------------------------------+++
# end 2023.03.08
# renamed
