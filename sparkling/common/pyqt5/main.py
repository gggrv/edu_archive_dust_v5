# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
# same project

def get_QItemSelection_rowilocs( item_selection ):
    
    # Extracts rowilocs from QItemSelection.
    
    # TODO:
    # add option for colilocs and both rowilocs & colilocs
    
    rowilocs = []
    
    for v in item_selection:
        
        start = v.topLeft().row()
        end = v.bottomRight().row() + 1 # include the end as well
        
        if start==end:
            rowilocs.append( start )
            
        else:
            rowilocs.extend( list(range(start,end)) )
            
    return rowilocs

def clear_layout( layout ):

    # help:
    # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt

    while layout.count():

        w = layout.takeAt(0)
        if w.widget() is not None:
            w.widget().deleteLater()
        elif w.layout() is not None:
            clear_layout( w.layout() )
                
def mime2file( mimeData ):
    
    # obtain paths
    paths = [ url.toLocalFile() for url in mimeData.urls() ]
    # normalize paths for current os
    return [  os.path.normpath(path) for path in paths ]
            
#---------------------------------------------------------------------------+++
# end 2022.05.26
# added get_QItemSelection_rowilocs
