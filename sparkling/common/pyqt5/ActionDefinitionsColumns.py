# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtGui import ( QIcon )
from PyQt5.QtWidgets import QAction
# same project
from sparkling.common.BaseColumns import BaseColumns

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

class ColumnsActionDefinitions( BaseColumns ):
    
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
    remove = 'remove'
    
    @staticmethod
    def convert_action_definitions( widget, action_definitions ):
        
        # Creates `QAction` objects from definitions.
        
        # Currently `action_definitions` is a `list of dict`.
        # I keep this architecture rather
        # then a `dict of dict`, because I want to preserve order -
        # `dict` is unordered. I may switch to
        # an `ordered dict of unordered dict` architecture
        # in the future.
        
        acts = []
        for row in action_definitions:
            
            action = ActionDefinitionObject(
                row, parent=widget
                )
            
            acts.append( action )
                
        return acts
    
    @staticmethod
    def remove_actions( widget, identities=None ):
        
        # Removes existing actions from a widget.
        # `identities` is either `None` or `list of str`.
        
        if identities is None:
            # remove all actions indiscriminately
            for act in widget.actions():
                widget.removeAction( act )
            return
        
        # remove only specific actions
        # this functionality overlaps with `modify actions`
        
        for act in widget.actions():
            if act.get_identity() in identities:
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
        
        # Whenever I want to modify existing actions,
        # I don't care about their order.
        # This means that having `modifications` as `list of dict`
        # is unnecessary. For ease of use and consistency I want
        # `modifications` to be in the same format as
        # `action definitions`. Currently it is `list of dict`.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        # iterate context menu
        for act in widget.actions():
            
            identity = act.get_identity()
            
            # iterate modifications
            # TODO
            # switch to `ordered dict of unordered dict`
            # to avoid multiple loops
            for mod in modifications:
                if identity in mod[c.identity]:
                    # this is the action i'm looking for
                    if c.remove in mod:
                        widget.removeAction( act )
                    else:
                        act.accept_modification( mod )
                    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# added another `remove` command
