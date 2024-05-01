# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
from time import sleep
import os
# pip install
import moosegesture
import pyautogui
from PyQt5.QtCore import ( QThread, pyqtSignal, Qt, QEvent )
from PyQt5.QtGui import ( QFont )
from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QLabel )
# same project
from sparkling.common.pyqt5.parentless.MainWindow import (
    MainWindow as ParentlessMainWindow )
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions
   
FOLLOWINDOW_MANUAL = """What to do?
1) Hold right mouse button.
2) Draw something while holding right mouse button.
"""

def ellipse_equation( x,y,a,b ):
    result = (x*x)/(a*a) + (y*y)/(b*b)
    return result

def followindow_is_too_far( w ):

    # get coordinates
    half_width, half_height = w.width()//2, w.height()//2
    current_x, current_y = w.x()+half_width, w.y()+half_height
    mouse_x, mouse_y = pyautogui.position()

    aa,bb = w.CHASE_DISTANCE_X, w.CHASE_DISTANCE_Y
    calculated_ellipse = ellipse_equation(
        current_x-mouse_x, current_y-mouse_y, aa+aa, bb+bb )

    if calculated_ellipse>1: return True
    return False

def followindow_enlarge( w ):

    # Show enlarged window, mouse in the middle.

    current_x,current_y = w.x(), w.y()
    new_w, new_h = w.BIGGER_DIMS_X, w.BIGGER_DIMS_Y
    w.resize( new_w, new_h )
    w.move( current_x-new_w//2, current_y-new_h//2 )

def followindow_shrink( w ):

    # Show small window near the mouse.
    
    # hide custom label
    w.Gui.lab.setVisible( False )

    current_w,current_h = w.width(),w.height()
    current_x,current_y = w.x(), w.y()
    new_w,new_h = w.SMALLER_DIMS_X, w.SMALLER_DIMS_Y
    w.resize( new_w,new_h )
    w.move( current_x+current_w//2, current_y+current_h//2 )

class MouseMonitorThread( QThread ):
    
    # This is a simple thread that constantly
    # emits mouse coordinates.

    # help:
    # https://nikolak.com/pyqt-threading-tutorial/

    MOUSE_COORDS = pyqtSignal( tuple )

    def __init__( self ):
        QThread.__init__(self)

    def __del__( self ):
        self.wait()

    def run( self ):
        
        while self.isRunning():
            self.MOUSE_COORDS.emit( pyautogui.position() )
            sleep(0.01)
        
class HungryWidget( QLabel ):
    
    # This widget can be customized in any way - change class inheritance,
    # inner contents, layouts, whatever.
    
    # This widget has only two uses:
    # 1) it becomes visible when smth is dragged to the followindow
    # 2) it becomes invisible when smth is not dragged to the followindow.

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( HungryWidget, self ).__init__( parent, *args, **kwargs )

        self.setObjectName( 'HungryWidget_grimoire' )
        self.setText( '     Θ     Θ     \nVVVVVVVVVVVVVVVVV\n\n\n\n\n\n\n\n\n\n\n\n\nЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛЛ' )
        self.setFont( QFont('Consolas', 12) )

class Followindow( QWidget ):
    
    # Small window which follows the mouse, accepts drops,
    # accepts mouse gestures.

    OK_TO_CLOSE = pyqtSignal( str )

    REQUEST_PATH_EATER = pyqtSignal( list )
    REQUEST_GESTURE_COMMAND = pyqtSignal( QWidget, list )
    REQUEST_MANUAL = pyqtSignal( QWidget )
    
    # where to stop near the mouse
    MOUSE_DISTANCE_X = 80
    MOUSE_DISTANCE_Y = 80
    # when to chase after mouse
    CHASE_DISTANCE_X = 85
    CHASE_DISTANCE_Y = 85
    # when enlarged
    BIGGER_DIMS_X = 300
    BIGGER_DIMS_Y = 300
    # when small
    SMALLER_DIMS_X = 5
    SMALLER_DIMS_Y = 5

    __mouse_coord_history = None
    
    class Gui:
        bg = None
        hungry_widget = None
        lab = None

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( Followindow, self ).__init__( parent, *args, **kwargs )
        
        self.__mouse_coord_history = []

        # layout
        lyt = QVBoxLayout()
        lyt.setContentsMargins(0,0,0,0)

        # background widget
        # without it followindow doesnt accept drops
        self.Gui.bg = QWidget( parent=self )

        # hidden hungry widget
        self.Gui.hungry_widget = HungryWidget( parent=self.Gui.bg )
        self.Gui.hungry_widget.setVisible( False )
        
        # hidden label for text display
        self.Gui.lab = QLabel( parent=self )
        self.Gui.lab.setVisible( False )

        # assemble
        
        bg_lyt = QVBoxLayout()
        bg_lyt.setContentsMargins(0,0,0,0)
        bg_lyt.addWidget( self.Gui.lab )
        self.Gui.bg.setLayout( bg_lyt )
        
        lyt.addWidget( self.Gui.bg )
        
        self.setLayout( lyt )
        
        # i must call self.show() at least once,
        # because if i use .show() from another
        # object, dropping items with mouse on the
        # followindow does not work.
        # this behaviour heavily depends on the window flag
        # QtCore.Qt.SplashScreen
        self.show()

        # i must call the following lines from the constructor,
        # because otherwise dropping items with mouse on the
        # followindow does not work.
        # this behaviour heavily depends on the window flag
        # Qt.SplashScreen
        #"""
        self.setWindowFlags(
            Qt.FramelessWindowHint # no frame
            | Qt.WindowStaysOnTopHint
            | Qt.SplashScreen # no taskbar entry
            )
        #"""
        
        self.setAcceptDrops(True)

    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
        
    def dragEnterEvent( self, ev ):

        # help:
        # https://www.tutorialspoint.com/pyqt5/pyqt5_drag_and_drop.htm

        self.__hungry_widget.setVisible(True)

        followindow_enlarge(self)

        ev.accept()

    def dropEvent( self, ev ):

        self.__hungry_widget.setVisible(False)
        
        followindow_shrink(self)

        # process drops

        if ev.mimeData().hasUrls():

            if 'file:///' in ev.mimeData().text():

                # obtain paths
                paths = [ url.toLocalFile() for url in ev.mimeData().urls() ]
                # normalize paths for current os
                paths = [  os.path.normpath(path) for path in paths ]

                self.REQUEST_PATH_EATER.emit( paths )
                
                ev.accept()
                
            # TODO url

    def dragLeaveEvent( self, ev ):

        self.__hungry_widget.setVisible(False)

        followindow_shrink(self)

        ev.accept()

    def mousePressEvent( self, ev ):
        pass

    def mouseReleaseEvent( self, ev ):

        if len( self.__mouse_coord_history )>0:
            
            gesture = moosegesture.getGesture(
                self.__mouse_coord_history )
            self.__mouse_coord_history = []
            self.REQUEST_GESTURE_COMMAND.emit( self, gesture )
            
        else:
            self.REQUEST_MANUAL.emit( self )

    def mouseMoveEvent( self, ev ):

        # help:
        # https://stackoverflow.com/questions/46147290/pyqt5-check-if-mouse-is-held-down-in-enter-event

        if ev.buttons() & Qt.RightButton:
            # im drawing a gesture with right mouse button
            
            self.__mouse_coord_history.append(
                pyautogui.position()
                )
            
        elif ev.buttons():
            # i'm drawing something with some other buttons
            self.REQUEST_MANUAL.emit( self )
            
        # i'm just hovering the mouse
        
class MainWindow( ParentlessMainWindow ):

    # Usually this window is invisible.
    # Controls followindow positioning and quantity.
    # For now I expect only one followindow.

    OK_TO_CLOSE = pyqtSignal( str )
    REQUEST_CUSTOM_PROGRAM = pyqtSignal( str )
    
    # mouse monitor thread
    __mmt = None

    def __init__( self,
                  own_doer,
                  parent=None,
                  *args, **kwargs ):
        super( MainWindow, self ).__init__(
            own_doer, parent=parent, *args, **kwargs )
        
        # i want to hide this window
        self.setWindowTitle( 'Main Window — followindow' )
        self.setVisible( False )
        
    def autorun( self, host_app ):
        
        # add custom menus to tray
        
        # short name for convenience
        c = ColumnsActionDefinitions
        
        actions = [
            {
                c.identity: 'dust/host/tray/toggle_followindow',
                c.text: 'Toggle followindow',
                c.method: self.tray_menu_toggle,
                c.icon: self._own_doer.Files.ICON,
                },
            ]
        
        c.add_actions( host_app.Gui.tray_button.contextMenu(), actions )
        
        # allow to launch custom programs
        # via followindow
        self.REQUEST_CUSTOM_PROGRAM.connect(
            host_app._request_custom_program_event )

        # autostart followindow
        self.tray_menu_toggle()
        
    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!

    def eventFilter( self, ob, ev ):

        # help:
        # https://stackoverflow.com/questions/52291734/pyqt5-mouse-hover-functions

        #print( 'eventfilter', ob, ev.type() )

        # what to do with follower windows
        if type(ob)==Followindow:

            if ev.type()==QEvent.Enter: # 10
                # when the cursor is inside followindow, i dont need to
                # monitor mouse position
                if self.__mmt is not None: self.__mmt.terminate()
                followindow_enlarge( ob )
            elif ev.type()==QEvent.Leave: # 11
                # when the cursor is outside of followindow, i do need
                # to monitor mouse position
                if self.__mmt is not None: self.__mmt.start()
                followindow_shrink( ob )
            """
            elif ev.type()==QEvent.DragEnter:
                print('dragenter')
            elif ev.type()==QEvent.DragLeave:
                print('dragleave')
            elif ev.type() == QEvent.Show: # 17
                #x,y = ob.optimal_position_near_mouse(self.mouse_x,self.mouse_y)
                #ob.relocate(x,y)
                pass
            elif ev.type() == QEvent.WinIdChange: # 203
                print( 'WinIdChange' )
            elif ev.type() == QEvent.WindowIconChange: # 34
                print( 'WindowIconChange' )
            elif ev.type() == QEvent.Move: # 13
                print( 'Move' )
            elif ev.type() == QEvent.Resize: # 14
                print( 'Resize' )
            elif ev.type() == QEvent.ShowToParent: # 26
                print( 'ShowToParent' )
            elif ev.type() == QEvent.PolishRequest: # 74
                print( 'PolishRequest' )
            elif ev.type() == QEvent.UpdateLater: # 78
                print( 'UpdateLater' )
            elif ev.type() == QEvent.UpdateRequest: # 77
                print( 'UpdateRequest' )
            """

        return super(MainWindow,self).eventFilter( ob, ev )

    def __reposition_followindows( self, mouse_coords ):
        
        # If there is more then one followindow, they will end up
        # at the same location, overlapping each other.

        for w in self._parentless_windows:
            
            if type(w)==Followindow:
            
                if followindow_is_too_far( w ):
    
                    x = mouse_coords[0]-w.MOUSE_DISTANCE_X
                    y = mouse_coords[1]-w.MOUSE_DISTANCE_Y
                    
                    w.move( x,y )

    def __spawn_followindow( self ):

        # Spawns a single visible followindow.

        w = Followindow( parent=None )
        self._register_parentless_window(w)
        
        w.setWindowTitle( 'followindow_%s'%w.objectName() )
        w.resize( w.SMALLER_DIMS_X, w.SMALLER_DIMS_Y )
        w.installEventFilter(self)
        
        #w.REQUEST_PATH_EATER.connect( self.__request_path_eater_event )
        w.REQUEST_GESTURE_COMMAND.connect( self.__request_gesture_command_event )
        w.REQUEST_MANUAL.connect( self.show_manual_event )
        
        w.show()
        
    def tray_menu_toggle( self ):
        
        # I want to toggle followindows on and off.
        # Unneeded followindows are destroyed.
        
        # help:
        # https://www.qtcentre.org/threads/28957-How-to-stop-QThread

        # find followindows, save references to them in a separate list
        followindows = []
        for w in self._parentless_windows:
            if type(w)==Followindow:
                followindows.append( w )

        # actually there were none
        if len(followindows)==0:
            
            log.debug( 'spawning and showing one followindow' )
            self.__spawn_followindow()

            log.debug( 'starting mouse monitor thread' )
            if self.__mmt is None:
                self.__mmt = MouseMonitorThread()
                self.__mmt.MOUSE_COORDS.connect( self.__reposition_followindows )
                self.__mmt.start()
                
            return
        
        # actually there were some, i want to toggle them off
            
        log.debug( 'terminating mouse monitor thread' )
        self.__mmt.MOUSE_COORDS.disconnect()
        self.__mmt.terminate()
        while not self.__mmt.isFinished(): pass # wait a little
        self.__mmt = None
        log.debug( 'mouse monitor thread is successfully terminated' )
        
        log.debug( 'removing all existing %s followindow(s)'%len(followindows) )
        for w in followindows:
            w.close() # trigger removal
            
    def _request_custom_program_event( self, custom_program_name ):
        
        self.REQUEST_CUSTOM_PROGRAM.emit( custom_program_name )
        
    def __request_gesture_command_event( self, followindow, gesture ):
        
        # Receives an array with a moosegesture, checks predefined
        # methods, runs suitable one.
        
        gestures = self._own_doer.get_gestures()
        
        for method, predefined_gesture in gestures.items():
            # iterate all known predefined gestures
            
            if gesture==predefined_gesture:
                
                if type(method)==str:
                    eval(method)
                else:
                
                    #try:
                    method()
                    #except Exception as ex:
                    #    print(ex) # TODO gui error display
                    
                # no need to check other gestures
                return
            
        # i end up here when i fail to find a predefined gesture
        log.error( f'unknown gesture: {gesture}' )
        followindow.Gui.lab.setText( 'Unknown gesture.' )
        os.startfile( self._own_doer.Files.CUSTOM_GESTURES )

    def show_manual_event( self, followindow ):
        
        # Is triggered by incorrect followindow input.
        
        followindow.Gui.lab.setText( FOLLOWINDOW_MANUAL )
        followindow.Gui.lab.setVisible( True )
            
    """
    def __request_path_eater_event( self, paths ):
        
        # I want to open path eater with some paths.
        # This usually means that I intend to add
        # said paths to the grimoire.
        
        from sparkling.path_eater.PathEater \
            import PathEater as widget_class
        w = widget_class(
            parent=None,
            paths=paths
            )
        self._register_parentless_window(w)
        w.show()
    """

#---------------------------------------------------------------------------+++
# end 2023.05.25
# shows manual when user input is chaoticc
