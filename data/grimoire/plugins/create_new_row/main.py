# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
from datetime import datetime
# pip install
# same project
from sparkling.common.pyqt5.main import append_actions

g_grimoire_main_window = None
PLUGIN_NAME = 'create_new_row'

def new_row( *args ):
    
    # Allows to create an empty new row in current playlist viewer.
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, can\'t create new row' )
        return
    
    now = datetime.now()
    date_human = now.strftime('%Y.%m.%d %X')
    
    # send to db, view
    metadata = {
        'timestamp': date_human
        }
    
    playlist_viewer._accept_custom_metadata( metadata )
    
def autoenable( grimoire_main_window ):
    
    global g_grimoire_main_window
    g_grimoire_main_window = grimoire_main_window
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, failed to enable' )
        return
        
    # mod context menu
    actions = [
        { # replaces new row
            'text': 'Add new row',
            'method': new_row,
            'shortcut': 'Ctrl+N',
            'owner': PLUGIN_NAME
            }
        ]
    
    append_actions( playlist_viewer, actions )
    
def autodisable( grimoire_main_window ):
    
    # remove modded actions
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, nothing to disable' )
        return
    
    # iterate through available actions
    for act in playlist_viewer.actions():
        
        try:
        
            # check custom owner parameter to see if
            # the action is created by a plugin
            # TODO
            # subclass QAction??
            if act._owner == PLUGIN_NAME:
                playlist_viewer.removeAction( act )
                
        except AttributeError:
            
            # this action does not have custom owner parameter
            # this miens that it was not
            # created by any sort of plugin
            pass
        
#---------------------------------------------------------------------------+++
# end 2023.05.22
# created
