# -*- coding: utf-8 -*-
#Python class "Demo Host App". Copyright (C) 2023 Anna Anikina
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
import os
# pip install
from PyQt5.QtCore import ( QCoreApplication )
from PyQt5.QtGui import ( QIcon )
from PyQt5.QtWidgets import ( QApplication,
    QMenu, QSystemTrayIcon )
# same project
# main
from sparkling import MainPaths
# host app
from sparkling.host_app.MainDoer import MainDoer
from sparkling.host_app.pyqt5.MainWindow import MainWindow
from sparkling.host_app.pyqt5.ExceptionViewer import ExceptionViewer
# other
from sparkling.common import ( readf, unique_loc )
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions
    
class HostApp( QApplication ):

    # Host application.
    # Provides access to predefined PyQt5 programs from tray menu.
    # Can set global css style.
    # Can handle unhandled exceptions.

    # invisible spawned parentless windows will be saved here
    __parentless_windows = None # future list
    
    # various doers will be remembered here
    __SomeDoers = None # future dictionary
    
    # personal doer will be remembered here
    __OwnDoer = None
    
    class Files:
        CSS = 'app.css'
        ICON_TRAY = 'tray.png'
        
    class Folders:
        OWN_DOER = 'host_qtapp'
        
    class Gui:
        
        main_window = None
        tray_button = None
        _exception_dialog = None
    
    def __init__( self,
                  sys_argv,
                  root_log_handler=None,
                  *args, **kwargs ):
        super( HostApp, self ).__init__( sys_argv, *args, **kwargs )
        
        # initialize dynamic things
        self.__parentless_windows = []
        self.__SomeDoers = {}
        
        # create invisible main window for the application
        # otherwise it won't work
        self.Gui.main_window = MainWindow()
        
        # create hidden exception dialog
        # TODO
        # move this outside
        self.Gui._exception_dialog = ExceptionViewer( parent=None )
        if root_log_handler is None:
            log.error( 'please provide custom `root log handler` in order to see logs/errors via gui' )
        else:
            root_log_handler.label_widget = self.Gui._exception_dialog.label_widget
        
        # own doer
        self.Folders.OWN_DOER = MainPaths.set_folder( self.Folders.OWN_DOER )
        self.__OwnDoer = MainDoer( self.Folders.OWN_DOER )
        
        # paths
        self.Files.CSS = self.__OwnDoer.set_file( self.Files.CSS )
        self.Files.ICON_TRAY = self.__OwnDoer.set_file( self.Files.ICON_TRAY )

        # set global app style
        self.reload_css()
        
        # create button with menu in system tray
        self.__init_tray()

        # load custom pyqt5 programs here
        
        self._request_custom_program_event( 'followindow' )
        
    def launch_exception_dialog( self ):
        # TODO
        # write log to file
        # read last n rows of that file
        # create/destroy exception_dialog widget on demand
        # rather then keep it in memory
        self.Gui._exception_dialog.show()
        
    def mainloop_start( self ):
        
        # Without running this method, the app won't launch.
        
        self.exec_()
        self.mainloop_exit()

    def mainloop_exit( self ):
        log.debug( 'exited mainloop, now exiting app' )
        QCoreApplication.exit()
        
    def reload_css( self ):

        src = self.Files.CSS
        
        if not os.path.isfile( src ):
            log.error( f'css styles not found, proceeding without them: {src}' )
            return

        css = readf(src)
        
        self.setStyleSheet( css )

    def open_folder( self ):
        os.startfile( MainPaths.application_root() )

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

        c = ColumnsActionDefinitions
        menu = QMenu( parent=self.Gui.main_window )
        actions = [
            {
                c.identity: 'dust/host/tray/open_app_folder',
                c.text: 'Open application folder',
                c.method: self.open_folder,
                },
            {
                c.identity: 'dust/host/tray/reload_css',
                c.text: 'Reload .css',
                c.method: self.reload_css,
                },
            {
                c.identity: 'dust/host/tray/show_log',
                c.text: 'Show log',
                c.method: self.launch_exception_dialog,
                },
            {
                c.identity: 'dust/host/tray/close_app',
                c.text: 'Exit',
                c.method: self.mainloop_exit,
                },
            ]        
        c.add_actions( menu, actions )

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
        
        # I no longer need this parentless window.
        # I destroy the object and
        # remove reference to it.

        for iloc, w in enumerate(self.__parentless_windows):
            
            if w.objectName()==object_name:

                self.__parentless_windows.pop(iloc)
                w.destroy()
                w.deleteLater()
                del w
                # just die already
                return
            
    def __register_doer( self, unique_name, CustomDoer ):
        
        # I may want to remember a custom `SomeDoer`
        # that was created by some `custom_program` -
        # this way I will be able quickly open this `custom_program` again
        # when needed.
        
        self.__SomeDoers[unique_name] = CustomDoer
        
    def __remove_doer( self, unique_name ):
        # I no longer need to remember this custom `SomeDoer`.
        self.__SomeDoers.pop( unique_name )
            
    def _request_custom_program_event( self, unique_name ):
        
        # Opens predefined program.
        
        # Right now it requires that any extention has both
        # headless `MainDoer` and gui `MainWindow`.
        # `MainDoer.autorun` must return a tuple:
        # either ( True, 'ok blablabla/nothing' )
        # or ( False, 'explanation why' )
        
        # TODO
        # allow to manage SomeDoers in host app's main window
        # generalize this function so that
        # there are no dedicated `if`s
        
        # import both gui and headless
        if unique_name=='grimoire':
            from sparkling.grimoire.MainDoer import MainDoer as Md
            from sparkling.grimoire import MainWindow as Mw
        elif unique_name=='followindow':
            from sparkling.followindow.MainDoer import MainDoer as Md
            from sparkling.followindow import MainWindow as Mw
            
        # get doer
        if unique_name in self.__SomeDoers:
            # already exists
            CustomDoer = self.__SomeDoers[unique_name]
        else:
            # need to make new
            # create save folder
            preferred_folder = Md.PREFERRED_SAVE_DIR_NAME
            save_folder = MainPaths.set_folder( preferred_folder )
            # get doer
            CustomDoer = Md( save_folder )
            
        # autorun headless
        # will be saved
        success, message = CustomDoer.autorun()
        if not success:
            log.error( f'headless part of the {unique_name} failed to initialize, no need to load gui' )
            return
        
        # headless ok, can proceed
        
        # autorun gui
        # will be destroyed
        w = Mw( CustomDoer, parent=None )
        w.autorun( self )
        
        # at this point everything initialised correctly,
        # remember
        self.__register_parentless_window( w )
        self.__register_doer( unique_name, CustomDoer )

#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here
