# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Contains common context-unaware functions for PyQt5.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
#from PyQt5.QtCore import ( Qt )
from PyQt5.QtWidgets import ( QAction, QTreeWidgetItemIterator )
# same project

def remove_actions( widget ):
    
    # Removes existing actions if they are present.
    
    for act in widget.actions():
        widget.removeAction( act )
        
def convert_action_definitions( widget, action_definitions ):
    
    act_objects = []
    
    for row in action_definitions:
        
        if type( row )==QAction:
            act_objects.append(row)
        else:
            action = QAction(
                row['text'], parent=widget
                )
            
            if 'shortcut' in row:
                action.setShortcut( row['shortcut'] )
            if 'method' in row:
                action.triggered.connect( row['method'] )
            
            act_objects.append( action )
            
    return act_objects

def append_actions( widget, action_definitions ):
    
    # Creates action objects based on provided definitions.
    
    act_objects = convert_action_definitions( widget, action_definitions )
    widget.addActions( act_objects )
            
def set_actions( widget, action_definitions ):
    
    # Replaces action objects based on provided definitions.
    
    remove_actions( widget )
    append_actions( widget, action_definitions )

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
# end 2022.08.26
# removed tree clearing
