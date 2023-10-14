# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Entry point. Launches `host application`.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import sys
import traceback
# pip install
# same project
# host app
from sparkling.host_app.pyqt5.HostApp import HostApp

# this variable will store the app
# currently unused
HOST_APPLICATION = None
    
class GuiLogHandler( logging.Handler ):
    
    # I want to see logs in GUI. This handler
    # attempts to do so.
    
    # i will set it externally
    # i expect `QPlainTextEdit`
    label_widget = None
    
    def __init__( self,
                  *args, **kwargs ):
        super( GuiLogHandler, self ).__init__(
            *args, **kwargs )
        
        #self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
    def emit( self, record ):
        
        msg = self.format( record )
        
        if not self.label_widget is None:
            #self.label_widget.setText( '\n'.join([ self.label_widget.text(),msg ]) )
            self.label_widget.appendPlainText( msg )

def _custom_excepthook( ex_type, ex_value, ex_traceback ):
    
    # I want to catch and log all unhandled exceptions - I want
    # the app to keep running even when unknown errors occur.
    # This function allows to do so, provided that the
    # app initialised correctly.
    
    # help:
    # https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
    # https://stackoverflow.com/questions/55819330/catching-exceptions-raised-in-qapplication

    # make sure keyboard interrupt is accessible to
    # user
    if issubclass( ex_type, KeyboardInterrupt ):
        sys.__excepthook__( ex_type, ex_value, ex_traceback )
        return
    
    # send the error traceback to all log handlers,
    # so that my custom `GuiLogHandler` can receive it
    # and add it to gui
    text = '\n'.join( traceback.format_exception(ex_type,ex_value,ex_traceback) )
    log.error( text )
    
    # force show gui
    HOST_APPLICATION.launch_exception_dialog()
    
    # app keeps running as if nothing happened
    
def autorun():
    
    # configure root logger
    # and enable my custom handler
    # help:
    # https://stackoverflow.com/questions/59971542/add-custom-handler-to-log-root-level-with-logging-basicconfig
    
    custom_handler = GuiLogHandler()
    
    logging.basicConfig(
        level=logging.ERROR,
        #format=,
        handlers=[
            logging.StreamHandler(),
            custom_handler,
            ]
        )

    # process unhandled exception how i want them
    sys.excepthook = _custom_excepthook

    # start the app
    global HOST_APPLICATION
    HOST_APPLICATION = HostApp( sys.argv, root_log_handler=custom_handler )
    HOST_APPLICATION.mainloop_start()

if __name__ == '__main__':
    autorun()

#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
