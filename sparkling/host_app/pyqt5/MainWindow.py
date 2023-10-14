# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
from PyQt5.QtWidgets import ( QMainWindow )
#from sparkling.grimoire.host_app.CentralWidget import CentralWidget

class MainWindow( QMainWindow ):
    
    # Empty main window.
    # Must exist - otherwise app won't work.

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__( parent, *args, **kwargs )
        
        # contents
        #cw = CentralWidget( paren=self )
        #self.setCentralWidget( cw )
        
        # appearance
        self.setWindowTitle( 'HostApp Main Window — dust' )
        
        # currently don't need it
        self.setVisible( False )
        
#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
