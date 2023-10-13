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
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions

g_grimoire_main_window = None
PLUGIN_NAME = 'create_new_row'

def new_row( *args ):
    
    # Allows to create an empty new row in current playlist viewer.
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, can\'t create new row' )
        return
    
    # write some metadata
    
    now = datetime.now()
    date_human = now.strftime('%Y.%m.%d %X')
    
    param_dict = {
        'timestamp': date_human,
        }
    
    playlist_viewer._add_to_view_db( [param_dict], True )
    
def autoenable( grimoire_main_window ):
    
    global g_grimoire_main_window
    g_grimoire_main_window = grimoire_main_window
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, failed to enable' )
        return
        
    # mod context menu
    c = ColumnsActionDefinitions
    actions = [
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/add_new_row',
            c.text: 'Add new row',
            c.method: new_row,
            c.shortcut: 'Ctrl+N',
            },
        ]
    c.add_actions( playlist_viewer, actions )
    
def autodisable( grimoire_main_window ):
    
    # remove modded actions
    
    # get latest playlist viewer
    playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, nothing to disable' )
        return
    
    # remove modded context menu
    c = ColumnsActionDefinitions
    modifications = [
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/add_new_row',
            c.remove: True,
            },
        ]
    c.modify_actions( playlist_viewer, modifications )
        
#---------------------------------------------------------------------------+++
# end 2023.10.13
# updated for version 5.0
