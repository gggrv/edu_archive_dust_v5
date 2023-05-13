# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Example custom main window.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtCore import pyqtSignal
# same project
from sparkling.common.pyqt5.parentless.MainWindow import (
    MainWindow as ParentlessMainWindow )
from sparkling.common.pyqt5 import set_actions
from sparkling.grimoire.pyqt5.CentralWidget import CentralWidget
        
class MainWindow( ParentlessMainWindow ):
    
    # Main window of my complex PyQt5 application.

    OK_TO_CLOSE = pyqtSignal( str )

    def __init__( self,
                  own_doer,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__(
            own_doer, parent=parent, *args, **kwargs )
        
        cw = CentralWidget(
            self._own_doer,
            parent=self,
            )
        self.setCentralWidget( cw )
        
        self.setWindowTitle( 'Main Window — grimoire' )
        
        self.__init_menu()
        
    def autorun( self, host_app ):
        
        # Will be called externally.
        
        self.show()
        
    def __init_menu( self ):
        
        # I do it once upon init.
        
        bar = self.menuBar()
        
        m_view = bar.addMenu( 'View' )        
        actions = [
            {
                'text': 'Toggle sidebar',
                'method': self.toggle_sidebar,
                'shortcut': 'F4',
                },
            ]
        set_actions( m_view, actions )
        
    def toggle_sidebar( self ):
        
        cw = self.centralWidget()
        if cw is not None:
            visible = cw.Gui.split_vleft.isVisible()
            cw.Gui.split_vleft.setVisible( not visible )

    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
        
    """
    def load_plugin( self, _ ):
        
        # help:
        # https://www.geeksforgeeks.org/how-to-import-a-python-module-given-the-full-path/
        
        if self.__blackboard is None:
            msg = 'can\'t use plugins without blackboard, proceeding without them'
            log.error( msg )
            return
        
        plugin_dir = str(self.__conn.current_db)
        plugin_name = str(self.__conn.current_label)
        
        plugin_src = os.path.join(
            self.__conn.get_dedicated_root(),
            Paths.PLUGINS, plugin_dir, '%s.py'%plugin_name )
        
        if os.path.isfile( plugin_src ):
            spec = importlib.util.spec_from_file_location(
                plugin_name, plugin_src )
            self.current_plugin = importlib.util.module_from_spec( spec )
            spec.loader.exec_module( self.current_plugin )
            self.current_plugin.autorun( self )
            
        else:
            
            if self.current_plugin is not None:
                self.current_plugin.autokill()
    """
        
#---------------------------------------------------------------------------+++
# end 2023.05.11
# switched to standardised headless doer
