# -*- coding: utf-8 -*-
#Python class "Parentless Main Window". Allows to spawn and interact with any number of parentless PyQt5 windows during runtime. Copyright (C) 2022 Anna Anikina
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
from PyQt5.QtWidgets import QMainWindow
# same project
from sparkling.common import unique_loc
            
class MainWindow( QMainWindow ):
    
    # I will use it as base for my custom main windows
    # so that they all host parentless widgets
    # in an identical manner.
    
    # Supports own doer.
    
    # own custom doer will be saved here
    _own_doer = None
    
    # invisible spawned parentless windows will be saved here
    _parentless_windows = None # future list

    def __init__( self,
                  own_doer,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__( parent, *args, **kwargs )

        self._own_doer = own_doer
        
        self._parentless_windows = []
        
    def autorun( self, host_app ):
        
        # Will be called externally.
        
        pass
            
    def _register_parentless_window( self, w ):
        
        # I operate with many parentless windows.
        # They would disappear if no one referenced them.
        # Here I save those references.
        # This function may be called from my custom
        # ParentlessMainWindow subclass.
    
        w.setObjectName(
            '%s%s'%( w.objectName(), unique_loc() )
            )
        w.OK_TO_CLOSE.connect( self._remove_parentless_window_event )
        self._parentless_windows.append(w)

    def _remove_parentless_window_event( self, object_name ):
        
        # I no longer need this parentless dialog.
        # I destroy the object and
        # remove reference to it from self.dialogs.
        # This function must not be called from my custom
        # ParentlessMainWindow subclass - it is triggered
        # automatically whenever i command w.close().

        for iloc, w in enumerate(self._parentless_windows):
            
            if w.objectName()==object_name:

                self._parentless_windows.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                return
                
#---------------------------------------------------------------------------+++
# end 2022.05.11
# created from another file
