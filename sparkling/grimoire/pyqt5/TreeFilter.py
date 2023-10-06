# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
from PyQt5.QtCore import ( pyqtSignal, Qt )
from PyQt5.QtWidgets import ( QWidget, QComboBox,
    QVBoxLayout, )
# same project
from sparkling.common import readf_yaml
from sparkling.neo4j.NeoTreeView import (
    NeoTreeView, TreeModel, c, NODE, TreeNode )

class TreeFilter( QWidget ):
    
    conn = None
    db_name = None

    class Gui:
        rules_cbx = None
        tree_view = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( TreeFilter, self ).__init__( parent, *args, **kwargs )
        
        self.Gui.tree_view = NeoTreeView( parent=self )
        self.Gui.rules_cbx = QComboBox( parent=self )
        
        # assemble
        
        lyt = QVBoxLayout()
        lyt.setContentsMargins( 0,0,0,0 )
        
        lyt.addWidget( self.Gui.tree_view )
        lyt.addWidget( self.Gui.rules_cbx )
        
        self.setLayout( lyt )
        
        # autorun
        
        self.Gui.rules_cbx.addItem( 'labels' )
        
        self.rule = 'MATCH (n) RETURN DISTINCT labels(n)'
        
        self.populate_tree()
    
    def some_item_was_doubleclicked( self, index ):
        
        self.expandItemEvent( index )
        
    def expandItemEvent( self, index ):
        
        node = index.internalPointer()
        
    def populate_tree( self ):
        
        if self.conn is None:
            return
        
        #self.Gui.tree_view.switch_depth_level_data( rule )
        #self.Gui.tree_view.get_first_depth_level( self.Gui.tree_view._MODEL.root_node )
        
        self.Gui.tree_view.clear()
        
        root_node = TreeNode()
        
        response = self.conn.query(
            self.rule, db_name=self.db_name
            )
        
        for r in response:
            root_node.add_subnode(
                list( r.data().values() )
                )
            
        self.Gui.tree_view.switch_root_node( root_node )
        
    def conn_was_changed_event( self, conn ):
        self.conn = conn
        
    def db_name_was_changed_event( self, db_name ):
        self.db_name = db_name
        
#---------------------------------------------------------------------------+++
# end 2022.05.11
# wip