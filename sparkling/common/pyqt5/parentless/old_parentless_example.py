# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Example of parentless window functionality I use
# with splashscreen borderless windows.
# It allows me to close windows without triggering app exit.
# Do not inherit! Copy and paste, otherwise pyqtSignal won't work
# properly.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import ( pyqtSignal )
from PyQt5.QtWidgets import QWidget
# same project
from sparkling.common import unique_loc

class Parentless( QWidget ):
    
    # This object is meant for quick tests,
    # not for actual use in practice
    # because signals stop working as intended.

    OK_TO_CLOSE = pyqtSignal( str )
    
    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( Parentless, self ).__init__( parent, *args, **kwargs )

    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
            
class ParentlessHost( QWidget ):
    
    # This object is meant for quick tests,
    # not for actual use in practice
    # because signals stop working as intended.
    
    dialogs = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( ParentlessHost, self ).__init__( parent, *args, **kwargs )

        self.dialogs = []

    def registerDialog( self, w ):
        
        # I operate with many parentless windows.
        # They would disappear if no one referenced them.
        # Here I save those references.
    
        w.setObjectName(
            '%s%s'%( w.objectName(), unique_loc() )
            )
        w.OK_TO_CLOSE.connect( self.removeDialogEvent )
        self.dialogs.append(w)

    def removeDialogEvent( self, object_name ):
        
        # I no longer need this parentless dialog.
        # I destroy the object and
        # remove reference to it from self.dialogs.

        for iloc, w in enumerate(self.dialogs):
            
            if w.objectName()==object_name:

                self.dialogs.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                return
                
#---------------------------------------------------------------------------+++
# end 2022.07.30
# separated from another file
