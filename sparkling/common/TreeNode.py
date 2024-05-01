# -*- coding: utf-8 -*-
#BSD Zero Clause License
#
#Copyright (C) 2022 by Anna Anikina
#
#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted.
#
#THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project

def gen_recursive_file_tree( parent_node, root_dir ):
    
    # Helpful function that generates tree of files and subfolders
    # in given dir.
    
    # create node for given root dir
    rdn = parent_node.add_subnode(
        [ os.path.basename(root_dir) ],
        return_subnode=True
        )
    
    for item in os.listdir( root_dir ):
        
        src = os.path.join( root_dir,item )
        
        if os.path.isfile( src ):
            # reached leaves
            rdn.add_subnode( [item] )
            
        else:
            # found another branch
            gen_recursive_file_tree( rdn, src )
    
    # all leaves are processed
    return rdn
        
def recursive_print( root_node ):
    
    shift = ' '*root_node.depth_level
    print( shift + str(root_node.values) )
    
    for n in root_node.subnodes:
        recursive_print( n )

class TreeNode( object ):
    
    # help:
    # https://stackoverflow.com/questions/66706247/subclassing-qabstractitemmodel-to-display-nested-dict-data-as-a-tree
    
    values = None # will become an array
    subnodes = None # will become an array
    parent_node = None # will become another TreeNode
    depth_level = None
    
    def __init__( self,
                  values=None,
                  *args, **kwargs ):
        super( TreeNode, self ).__init__( *args, **kwargs )
        
        # new TreeNode is completely disconnected
        # from mundane world
        
        self.values = values if values else []
        self.subnodes = []
        self.depth_level = 0
        
    def __del__( self ):
        
        # When parent node is unreferenced,
        # unreference all subnodes as well.
        
        self.remove_subnodes( 0, n_subnodes=-1 )
        
    def __repr__( self ):
        
        shift = '%s %s ' % ( ' '*self.depth_level, str(self.depth_level) )
        text = shift + str( self.values )
        lines = []
        
        for n in self.subnodes:
            lines.append( '\n' + n.__repr__() )
            
        return text + ''.join(lines)
        
    def get_subnodeiloc( self, subnode ):
        return self.subnodes.index( subnode )
            
    def add_subnode( self, values, desired_subnodeiloc=None,
        return_subnode=False ):
            
        node = TreeNode( values=values )
        node.parent_node = self
        node.depth_level = self.depth_level+1
        
        if desired_subnodeiloc is None:
            
            self.subnodes.append( node )
            if return_subnode:
                return self.subnodes[ -1 ]
            
        else:
            
            self.subnodes.insert( desired_subnodeiloc, node )
            if return_subnode:
                return self.subnodes[ desired_subnodeiloc ]
        
    def remove_subnodes( self, subnodeiloc, n_subnodes=1 ):
        
        # Remove this many subnodes after this subnodeiloc.
        
        if n_subnodes<0: n_subnodes=len(self.subnodes)
        
        for _ in range(n_subnodes):
            # delete any sub-subnodes
            self.subnodes[subnodeiloc].remove_subnodes( 0, n_subnodes=-1 )
            # unfererence from parent
            self.subnodes[subnodeiloc].parent_node=None
            # unreference from this array
            self.subnodes.pop( subnodeiloc )
                
#---------------------------------------------------------------------------+++
# end 2022.08.28
# bug fix
