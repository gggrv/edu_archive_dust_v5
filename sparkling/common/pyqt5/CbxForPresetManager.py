# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QComboBox )
# same project
    
class CbxForPresetManager( QComboBox ):
    
    _preset_manager = None
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( CbxForPresetManager, self ).__init__(
            parent, *args, **kwargs )
        
        # Custom combobox that, along with a `screen name`,
        # stores current `preset name`.
        
    """
    def currentData( self, role=Qt.UserRole ):
        
        # Returns current preset name.
        
        if role == Qt.UserRole:
            return self.preset_name
    """
    
    def get_preset_columns( self ):
        return self._preset_manager.Columns
    
    def current_preset( self ):
        unique_name = self.currentData()
        return self._preset_manager.preset( unique_name )
        
    def set_preset_manager( self, preset_manager ):
        
        self._preset_manager = preset_manager
        
        self.reload_items()
        
    def reload_items( self ):
        
        # Does not trigger anything.
        
        self.blockSignals( True )
        
        self.clear()
        
        # make sure i have presets to show
        if self._preset_manager is None:
            return
        ps = self._preset_manager.presets()
        if len( ps ) == 0:
            return
        
        # short name for convenience
        c = self._preset_manager.Columns
        
        for preset_name, p in ps.items():
            self.addItem( p[c.screen_name], userData=preset_name )
    
        self.blockSignals( False )

#---------------------------------------------------------------------------+++
# end 2023.10.12
# created