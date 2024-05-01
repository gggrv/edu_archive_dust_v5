# -*- coding: utf-8 -*-
#Python utility "Combobox for Preset Manager". Allows to conveniently switch between existing presets via PyQt5 QComboBox. Copyright (C) 2023 Anna Anikina
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QComboBox )
# same project
    
class CbxForPresetManager( QComboBox ):
    
    # This custom ComboBox allows to easily switch
    # between `presets` within chosen
    # `preset manager`.
    
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