# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtWidgets import ( QWidget )
# same project

class CentralWidget( QWidget ):
    
    # Empty central widget.
    # Currently unused.
    # Can be easilt enabled in the `MainWindow.py`.

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( CentralWidget, self ).__init__( parent, *args, **kwargs )
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
