# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import importlib
import os
# pip install
from PyQt5.QtCore import pyqtSignal
# same project
from sparkling.common.pyqt5.parentless.MainWindow import (
    MainWindow as ParentlessMainWindow )
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions
from sparkling.grimoire.pyqt5.CentralWidget import CentralWidget, MULTIVALUE_SEPARATOR
        
# each plugin should have the following file
# with at least two methods: autoenable( parent_main_window ),
# autodisable( parent_main_window )
PLUGIN_ENTRY_FILE = 'main.py'

class MainWindow( ParentlessMainWindow ):
    
    # Main window of my complex PyQt5 application.
    
    # Regarding plugins and custom QActions (menu items):
    # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QAction.html#more
    # recommends that each QAction( parent=CorrespondingMainWindow ),
    # so grimoire plugins should be managed by this MainWindow class,
    # not the CentralWidget class.
    # Each plugin's autoenable() function will receive
    # a pointer to this MainWindow. This way each plugin will have access
    # to the whole widget architecture. Unsafe, useful.

    OK_TO_CLOSE = pyqtSignal( str )

    _own_doer = None
    
    # loaded plugins will be here
    # i can enable/disable them freely via gui
    # all plugins will be unloaded when i close the MainWindow
    _plugins = None # future dictionary
    
    def __init__( self,
                  own_doer,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__(
            own_doer, parent=parent, *args, **kwargs )
        
        # dynamic
        self._own_doer = own_doer
        self._plugins = {}
        
        # settings
        self.setWindowTitle( 'Main Window — grimoire' )
        
        # gui
        
        cw = CentralWidget(
            self._own_doer,
            parent=self,
            )
        self.setCentralWidget( cw )
        
        # signals
        
        cw.REQUEST_PLUGINS_DISABLE.connect( self.__request_plugins_disable_event )
        cw.REQUEST_PLUGINS_ENABLE.connect( self.__request_plugins_enable_event )
        
        self.__init_menu()
        
    def autorun( self, host_app ):
        
        # Will be called externally.
        
        self.show()
        
    def __init_menu( self ):
        
        # I do it once upon init.
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        bar = self.menuBar()
        
        m_edit = bar.addMenu( 'Edit' )        
        actions = [
            {
                c.identity: 'grimoire/main_window/edit/rename_selection',
                c.text: 'Rename selected files',
                c.method: self.launch_selection_renamer,
                c.shortcut: 'Alt+Left',
                },
            ]
        c.add_actions( m_edit, actions )
        
        m_view = bar.addMenu( 'View' )        
        actions = [
            {
                c.identity: 'grimoire/main_window/view/toggle_sidebar',
                c.text: 'Toggle sidebar',
                c.method: self.toggle_sidebar,
                c.shortcut: 'F4',
                },
            ]
        c.add_actions( m_view, actions )
        
    def toggle_sidebar( self ):
        
        cw = self.centralWidget()
        if cw is not None:
            visible = cw.Gui.split_vleft.isVisible()
            cw.Gui.split_vleft.setVisible( not visible )

    def closeEvent( self, ev ):
        self.centralWidget().wrap_up_before_closing_main_window()
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
        
    def __request_plugins_disable_event( self, plugin_names, requester ):
        
        # Removes this pugin's additional functionality
        # from playlist context menu, etc.
        
        # Right now I keep loaded plugins until grimoire's main
        # window is closed.
        
        for plugin_name in plugin_names.split( MULTIVALUE_SEPARATOR ):
        
            if not plugin_name in self._plugins:
                log.error( f'attempt to remove unloaded plugin functionality: {plugin_name}' )
                return
        
            self._plugins[plugin_name].autodisable( self, requester )
        
    def __enable_plugin( self, plugin_name, requester ):
        
        if plugin_name in self._plugins:
            # this plugin is already loaded
            # enable it again
            p = self._plugins[plugin_name].autoenable( self, requester )
            return
        
        # i need to load this plugin
        
        # load it
        plugin_src = os.path.join(
            self._own_doer.Folders.PLUGINS,
            plugin_name,
            PLUGIN_ENTRY_FILE
            )
        if not os.path.isfile( plugin_src ):
            log.error( f'plugin {plugin_name} not found at location {plugin_src}' )
            return
        spec = importlib.util.spec_from_file_location(
            plugin_name, plugin_src
            )
        if spec is None:
            log.error( f'failed to load invalid plugin {plugin_name}' )
            return
        p = importlib.util.module_from_spec( spec )
        spec.loader.exec_module( p )
        
        # remember
        self._plugins[plugin_name] = p
        
        # enable
        p.autoenable( self, requester )
        
    def __request_plugins_enable_event( self, plugin_names, requester ):
        
        # Adds this pugin's additional functionality
        # into playlist context menu, etc.
        
        # help:
        # https://www.geeksforgeeks.org/how-to-import-a-python-module-given-the-full-path/
        
        for plugin_name in plugin_names.split( MULTIVALUE_SEPARATOR ):
            self.__enable_plugin( plugin_name, requester )
        
    def launch_selection_renamer( self ):
        cw = self.centralWidget()
        if not cw is None:
            cw.launch_selection_renamer()
        
#---------------------------------------------------------------------------+++
# end 2023.10.12
# added `launch_selection_renamer`
