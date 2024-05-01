# -*- coding: utf-8 -*-
#Python utility "Grimoire Plugin". Allows to create a new row in a "Grimoire Playlist Viewer". Copyright (C) 2023 Anna Anikina
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
from datetime import datetime
# pip install
# same project
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions

PLUGIN_NAME = 'create_new_row'

# `QWidget` that requested this plugin
g_plugin_requester = None

def new_row( *args ):
    
    # Allows to create an empty new row in current playlist viewer.
    
    # get latest playlist viewer
    if g_plugin_requester is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, can\'t create new row' )
        return
    
    # write some metadata
    
    now = datetime.now()
    date_human = now.strftime('%Y.%m.%d %X')
    
    param_dict = {
        'timestamp': date_human,
        }
    
    g_plugin_requester._add_to_view_db( [param_dict], True )
    
def autoenable( grimoire_main_window, requester ):
    
    # remember
    global g_plugin_requester
    g_plugin_requester = requester
    
    # get latest playlist viewer
    #playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if g_plugin_requester is None:
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
    c.add_actions( g_plugin_requester, actions )
    
def autodisable( grimoire_main_window, requester ):
    
    # remove modded actions
    
    if g_plugin_requester is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, nothing to disable' )
        return
    
    # remove modded context menu
    c = ColumnsActionDefinitions
    act_identities = [
        f'grimoire/plugin/{PLUGIN_NAME}/add_new_row'
        ]
    c.remove_actions( requester, act_identities )
        
#---------------------------------------------------------------------------+++
# end 2023.10.19
# simplified
