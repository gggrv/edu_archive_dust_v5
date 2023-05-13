# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Host application.
# Provides access to predefined PyQt5 programs from tray menu.
# Can set global css style.

# logging
import logging
log = logging.getLogger(__name__)

log.setLevel( logging.DEBUG )

# embedded in python
import os
import sys
# pip install
from PyQt5.QtCore import ( QCoreApplication )
from PyQt5.QtGui import ( QIcon )
from PyQt5.QtWidgets import ( QWidget, QMainWindow, QApplication,
    QMenu, QSystemTrayIcon )
# same project
from sparkling import MainPaths
from sparkling.common import ( readf, unique_loc )
from sparkling.common.SomeDoer import ( SomeDoer as BaseSomeDoer )
from sparkling.common.pyqt5 import ( set_actions )

class CentralWidget( QWidget ):
    
    # Empty central widget.
    # Unused.

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( CentralWidget, self ).__init__( parent, *args, **kwargs )

class MainWindow( QMainWindow ):
    
    # Empty main window.
    # Must exist - otherwise app won't work.

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__( parent, *args, **kwargs )
        
        # TODO
        # should probably add custom central widget here
        # that allows install/delete subpackages,
        # file generation, etc
        
        self.setWindowTitle( 'HostApp Main Window — dust' )
        
        self.setVisible( False )

class OwnDoer( BaseSomeDoer ):
    
    PREFERRED_SAVE_DIR_NAME = 'host_qtapp'
    
    _generate_file_functions = {} # none are needed
        
    def __init__( self, save_folder ):
        
        super( OwnDoer, self ).__init__( save_folder )
    
class HostApp( QApplication ):
    
    # invisible spawned parentless windows will be saved here
    __parentless_windows = None # future list
    
    # standard managers for different custom programs
    # will be remembered here
    __doers = None # future dictionary
    
    __own_doer = None
    
    class Files:
        CSS = 'app.css'
        ICON_TRAY = 'tray.png'
        
    class Folders:
        PERSONAL_DATA = OwnDoer.PREFERRED_SAVE_DIR_NAME
        
    class Gui:
        
        main_window = None
        tray_button = None
    
    def __init__( self,
                  sys_argv,
                  *args, **kwargs ):
        super( HostApp, self ).__init__( sys_argv, *args, **kwargs )
        
        # initialize dynamic things
        self.__parentless_windows = []
        self.__doers = {}
        
        # create personal standard manager,
        # set folders and files
        self.Folders.PERSONAL_DATA = MainPaths.set_folder( self.Folders.PERSONAL_DATA )
        self.__own_doer = OwnDoer( self.Folders.PERSONAL_DATA )
        self.Files.CSS = self.__own_doer.set_file( self.Files.CSS )
        self.Files.ICON_TRAY = self.__own_doer.set_file( self.Files.ICON_TRAY )

        # create invisible main window for the application
        # otherwise it won't work
        self.Gui.main_window = MainWindow()

        self.reload_css()
        
        # create button with menu in system tray
        self.__init_tray()

        # load custom pyqt5 programs here
        
        self._request_custom_program_event( 'followindow' )
        
        # gui mainloop
        self.exec_()
        self.exit_mainloop()

    def reload_css( self ):

        src = self.Files.CSS
        
        if not os.path.isfile( src ):
            log.error( f'css styles not found, proceeding without them: {src}' )
            return

        # TODO
        # do it safely
        css = readf(src)
        
        self.setStyleSheet( css )

    def exit_mainloop( self ):
        log.debug( 'exited mainloop, now exiting app' )
        QCoreApplication.exit()

    def open_folder( self ):
        os.startfile( MainPaths.get_application_root() )

    def _tray_icon_was_activated( self, ev ):
        if ev==1: pass # right click
        elif ev==2: pass # double left click
        elif ev==3: pass # left click
        elif ev==4: pass # middle click

    def _show_tray_notification( self, title, text ):

        self.Gui.tray_button.showMessage(
            title,
            text,
            QSystemTrayIcon.Information,
            2000
            )

    def __init_tray( self ):
        
        # Creates an icon in system tray of icons.
        # Called once upon init.

        self.Gui.tray_button = QSystemTrayIcon(
            QIcon( self.Files.ICON_TRAY ), # can be absent
            parent=self.Gui.main_window
            )

        menu = QMenu( parent=self.Gui.main_window )
        
        actions = [
            {
                'text': 'Open application folder',
                'method': self.open_folder,
                },
            {
                'text': 'Reload .css',
                'method': self.reload_css,
                },
            #{
            #    'text': 'Generate missing data files',
            #    'method': self.reload_css,
            #    },
            {
                'text': 'Exit',
                'method': self.exit_mainloop,
                },
            ]
        
        set_actions( menu, actions )

        # assemble
        self.Gui.tray_button.setContextMenu( menu )
        self.Gui.tray_button.activated.connect( self._tray_icon_was_activated )

        # visibility
        self.Gui.tray_button.setVisible(True)
        self.Gui.tray_button.show()
        
    def __register_parentless_window( self, w ):
        
        # I operate with many parentless windows.
        # They would disappear if no one referenced them.
        # Here I save those references.
    
        w.setObjectName(
            '%s%s'%( w.objectName(), unique_loc() )
            )
        w.OK_TO_CLOSE.connect( self.__remove_parentless_window_event )
        self.__parentless_windows.append(w)

    def __remove_parentless_window_event( self, object_name ):
        
        # I no longer need this parentless dialog.
        # I destroy the object and
        # remove reference to it from self.dialogs.

        for iloc, w in enumerate(self.__parentless_windows):
            
            if w.objectName()==object_name:

                self.__parentless_windows.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                # just die already
                return
            
    def __register_doer( self, custom_doer, name ):
        self.__doers[name] = custom_doer
        
    def __remove_doer( self, k ):
        
        if not k in self.__doers:
            raise KeyError
            
        self.__doers.pop(k)
            
    def _request_custom_program_event( self, name ):
        
        # Opens predefined PyQt5 program, remembers some data.
        # Even if you close this custom program,
        # some necessary data will
        # be remembered.
        
        # TODO
        # allow to manage SomeDoers in host app's main window
        # generalize this function so that
        # there are no dedicated `if`s
        
        # import both gui and headless
        if name=='grimoire':
            from sparkling.grimoire.MainDoer import MainDoer as Md
            from sparkling.grimoire import MainWindow as Mw
        elif name=='followindow':
            from sparkling.followindow.MainDoer import MainDoer as Md
            from sparkling.followindow import MainWindow as Mw
            
        # get doer
        if name in self.__doers:
            # already exists
            custom_doer = self.__doers[name]
        else:
            # need to make new
            # create save folder
            pref_name = Md.PREFERRED_SAVE_DIR_NAME # static
            save_folder = MainPaths.set_folder( pref_name )
            # get doer
            custom_doer = Md( save_folder ) # object
            
        # autorun headless
        # will be saved
        custom_doer.autorun()
        
        # autorun gui
        # will be destroyed
        w = Mw( custom_doer, parent=None )
        w.autorun( self )
        
        # remember
        self.__register_parentless_window( w )
        self.__register_doer( custom_doer, name )

def autorun():
    ob = HostApp( sys.argv )

if __name__ == '__main__':
    autorun()

#---------------------------------------------------------------------------+++
# end 2023.05.13
# fixed recreating doer every time
