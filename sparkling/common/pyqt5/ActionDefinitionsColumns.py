# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Contains common context-unaware functions for PyQt5.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtGui import ( QIcon )
from PyQt5.QtWidgets import QAction
# same project

class ActionDefinitionObject( QAction ):
    
    # custom extension of functionality
    # of standard action
    
    # unique informative string with
    # predefined format that looks like this:
    # {designation}/{class}/{menu}/{action_purpose}
    # where
    # - `designation` is a subjective package name / something informative
    # - `class` is a subjective class name
    # - `menu` is a subjective menu type (File, Edit, View...)
    # - `action_purpose` is a subjective action description
    # i use this `identity` to uniquely identify
    # actions at runtime for various purposes
    __identity = None
    
    def __init__( self,
            action_definition,
            parent,
            *args, **kwargs ):
        
        super( ActionDefinitionObject, self ).__init__(
            parent=parent, *args, **kwargs )
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        # remember
        
        if c.identity in action_definition:
            self.__identity = action_definition[c.identity]
            
        self.accept_modification( action_definition )
            
    def get_identity( self ):
        return self.__identity
    
    def accept_modification( self, action_definition ):
        
        # short name for convenience
        row = action_definition
        c = ColumnsActionDefinitions
        
        # i assume that identity check was already performed
        
        if c.text in row:
            self.setText( row[c.text] )
        if c.shortcut in row:
            self.setShortcut( row[c.shortcut] )
        if c.method in row:
            self.triggered.connect( row[c.method] )
        if c.enabled in row:
            self.setEnabled( row[c.enabled] )
        if c.visible in row:
            self.setVisible( row[c.visible] )
        if c.icon in row:
            icon = QIcon( row[c.icon] )
            self.setIcon( icon )

class ColumnsActionDefinitions:
    
    # For some arbitrary data I usually write either
    # - a custom `Preset` class (inherits from `PresetManager`)
    # - a custom `Columns` class (always static, may inherit some other `Columns`).
    
    # Any given `action definition` could
    # possibly have been a `Preset`.
    # Due to the fact that `action definitions` are
    # inconvenient to have in separate text files,
    # I use `Columns` as a simplified `Preset`.
    
    # TODO
    # support not only actions, but also
    # menus
    
    identity = 'identity'
    text = 'text'
    method = 'method'
    shortcut = 'shortcut'
    enabled = 'enabled'
    visible = 'visible'
    icon = 'icon'
    
    @staticmethod
    def convert_action_definitions( widget, action_definitions ):
        
        # Creates `QAction` objects from definitions.
        
        acts = []
        for row in action_definitions:
            
            action = ActionDefinitionObject(
                row, parent=widget
                )
            
            acts.append( action )
                
        return acts
    
    @staticmethod
    def remove_actions( widget ):
        
        # Removes existing actions from a widget.
        
        # TODO
        # parametrize to remove specific identities
        
        for act in widget.actions():
            widget.removeAction( act )
    
    @staticmethod
    def add_actions( widget, action_definitions ):
        
        # Creates action objects based on provided definitions.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        act_objects = c.convert_action_definitions( widget, action_definitions )
        widget.addActions( act_objects )
              
    @staticmethod
    def modify_actions( widget, modifications ):   
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        # iterate context menu
        for act in widget.actions():
            
            identity = act.get_identity()
            
            for mod in modifications:
                if identity in mod[c.identity]:
                    act.accept_modification( mod )
                    
#---------------------------------------------------------------------------+++
# end 2023.10.07
# moved `modify_actions` here
