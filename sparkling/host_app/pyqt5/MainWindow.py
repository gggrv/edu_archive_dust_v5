# -*- coding: utf-8 -*-
#BSD Zero Clause License
#
#Copyright (C) 2023 by Anna Anikina
#
#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted.
#
#THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
