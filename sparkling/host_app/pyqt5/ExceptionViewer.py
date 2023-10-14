# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Custom pyqt5 widgets for handling logs.
# help:
# https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QDialog, QVBoxLayout,
    QPlainTextEdit )
# same project

class ExceptionViewer( QDialog ):
    
    # This is a floating dialog that
    # informs the user about any
    # unhandled exceptions
    # that might be happening.

    OK_TO_CLOSE = pyqtSignal( str )
    
    # this widget will be remembered and updated in
    # the custom log handler
    label_widget = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( ExceptionViewer, self ).__init__(
            parent, *args, **kwargs )
        
        # appearance
        self.setWindowTitle( 'HostApp Exception Log — dust' )
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            )
        
        # gui

        self.label_widget = QPlainTextEdit( parent=self )
        self.label_widget.setReadOnly( True )
        self.label_widget.setMinimumWidth( 1000 )
        self.label_widget.setMinimumHeight( 400 )
        self.label_widget.setStyleSheet( 'font-family: consolas; text-size: 2.5pt; text-alignment: left; color: white;' )

        # assemble
        
        lyt = QVBoxLayout()
        lyt.addWidget( self.label_widget )
        self.setLayout( lyt )
        
    def closeEvent( self, ev ):
        #self.OK_TO_CLOSE.emit( self.objectName() )
        self.hide()
        ev.ignore() # !!!
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
