# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Everything needed for custom pandas table view.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import re
# pip install
import pandas as pd
from PyQt5.QtCore import ( Qt, pyqtSignal )
# same project
from sparkling.common.pyqt5 import ( set_actions )
from sparkling.common.TreeNode import TreeNode
from sparkling.common.pyqt5.TreeModel import TreeModel
from sparkling.common.pyqt5.TreeView import TreeView
from sparkling.neo4j.Columns import Columns as c, NODE

def get_progressive_filter( fields_to_filter_by, chosen_tree_node ):
    
    # Creates progressive filter for chosen tree node.
    
    # how many columns were already expanded?
    their_values = [] # they will be backwards
    node = chosen_tree_node
    while node.parent_node is not None:
        # move upwards from the chosen node
        # until i reach the root
        their_values.append( node.values[0] )
        node = node.parent_node
    del node
        
    # i want to filter them!
    
    conditions = []
    
    for coliloc, value in enumerate( their_values[::-1] ):
        col = fields_to_filter_by[coliloc]
        if value==NeoTreeView.Strings.MISSING_VALUE:
            condition = f'{c.NODE}.{col} IS NULL'
            conditions.append( condition )
        else:
            value = re.sub( r'([\\\"\'])', r'\\\1', value )
            condition = f'{c.NODE}.{col} = \'{value}\''
            conditions.append( condition )
    
    # obtain full command
    return ' AND '.join( conditions )

class NeoTreeView( TreeView ):
    
    SEND_TO_PLAYLIST = pyqtSignal( pd.DataFrame )
    
    class Strings:
        
        MISSING_VALUE = '< NO DATA >'
        SEND_TO_PLAYLIST = 'Send selection to current playlist'
    
    conn = None
    db_name = None
    
    depth_level_data = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( NeoTreeView, self ).__init__(
            parent=parent, *args, **kwargs )
        
        self.setContextMenuPolicy( Qt.ActionsContextMenu )
        
        self.switch_model( TreeModel() )
        
        # autorun
        
        self._init_context_menu()
        
        self.switch_root_node( TreeNode() )
        #self.get_first_depth_level( self._MODEL.root_node )
        
    """
    def switch_depth_level_data( self, depth_level_data ):
        if type( depth_level_data ) is list:
            self.depth_level_data = depth_level_data
        else:
            self.depth_level_data = None
        
    def get_first_depth_level( self, chosen_node ):
    
        # Obtain node text of proper depth.
        
        if not self.conn.is_valid():
            return
        if self.depth_level_data is None:
            return
        
        depth_level = chosen_node.depth_level
        if depth_level>=len( self.depth_level_data ):
            # ive already went as deep as possible
            return
        
        col = self.depth_level_data[ depth_level ]
        
        # obtain command
        
        node = self.conn.convert_node(
            c.NODE, self.conn.current_label
            )
        
        command = None
        if depth_level==0:
            # this is top-level item
            command = f'MATCH {node} RETURN DISTINCT {c.NODE}.{col}'
        else:
            # this is nested item
            conditions = get_progressive_filter(
                self.depth_level_data, chosen_node )
            command = f'MATCH {node} WHERE {conditions} RETURN DISTINCT {c.NODE}.{col}'
        
        # obtain response
        
        response = self.conn.query(
            command, db_name=self.db_name )
        
        if response is None:
            # nothing to append chosen node with
            return
        
        # obtain data
        
        rows = []
        col = self.depth_level_data[ depth_level ]
        for record in response:
            rows.append( record[ f'{c.NODE}.{col}' ] )
        
        # append to tree
        
        self._MODEL.layoutAboutToBeChanged.emit()
        
        # delete existing
        chosen_node.remove_subnodes( 0, -1 )
        
        texts = list(
            pd.Series(rows).fillna(
                NeoTreeView.Strings.MISSING_VALUE
                ).astype(str).sort_values().unique()
            )
        for text in texts:
            chosen_node.add_subnode(
                [ text ]
                )

        self._MODEL.layoutChanged.emit()
    """
                
    def _init_context_menu( self ):
        
        actions = [
            {
                'text': NeoTreeView.Strings.SEND_TO_PLAYLIST,
                'method': self.selection_send,
                },
            ]
        
        set_actions( self, actions )
        
    def selection_send( self ):
        
        # Downloads dataftame based on chosen node
        # progressive filter
        # and sends it somewhere.
        
        selection = self.selected_nodes()
        if len(selection)==0: return
        
        # for now i can send only one node
        # sending multiple would require additional complex checks
        top_selection = selection[0]
        del selection
        
        # obtain command
        
        label = ':'.join([ v.strip() for v in top_selection.values[0] ])
        if len(label)==0: label=''
        
        # obtain df
            
        response = self.conn.query(
            f'MATCH (n:{label}) RETURN n' if len(label)>0 else f'MATCH (n) WHERE labels(n) = [] RETURN n',
            db_name=self.db_name
            )
        if response is None: return
        
        df = self.conn.response2df( response )
        
        self.SEND_TO_PLAYLIST.emit( df )
        
    def conn_changed_event( self, conn ):
        self.conn = conn
        
#---------------------------------------------------------------------------+++
# end 2023.05.11
# wip