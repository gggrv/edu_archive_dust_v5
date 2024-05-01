# -*- coding: utf-8 -*-
#Python utility "Grimoire Plugin". Allows to delete empty folders from a custom root folder via a "Grimoire Playlist Viewer". Copyright (C) 2023 Anna Anikina
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
# same project
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions, BaseColumns
from sparkling.common import delete_empty_folders

PLUGIN_NAME = 'remove_empty_folders'

# `QWidget` that requested this plugin
G_PLAYLIST_VIEWER = None

G_PLUGIN_INITIALIZED = False
G_PLUGIN_SETTINGS = None
    
class ColumnsPluginSettings( BaseColumns ):
    
    # Plugin settings can be remembered in `db` as `node` `paremeter`
    # named `PLUGIN_SETTINGS_FIELD_NAME`.
    # TODO
    # validate contents so that neo4j never fails to
    # write this data to server
    
    # i will add this to playlist `settings` dict
    PLUGIN_SETTINGS_FIELD_NAME = 'gp_remove_empty_folders'
    
    root_folder = 'root_folder'
    
    @classmethod
    def parse_plugin_settings( cls, plugin_settings ):
        
        # short name for convenience
        text = plugin_settings
        
        did_change = False
        
        # force new
        if text == '':
            
            did_change = True
            
            return {
                cls.root_folder: '<please paste full path to some folder here>',
                }, True
            
        # attempt to parse
        settings = {}
        
        for item in text.split(';'):
            key, value = item.split(':',maxsplit=1)
            settings[key] = value
            
        return settings, did_change
        
    @classmethod
    def get_plugin_settings( cls, playlist_settings ):
        
        # Will eithre parse/validate existing,
        # or create new ones from scratch.
        
        need_new = False
        if not cls.PLUGIN_SETTINGS_FIELD_NAME in playlist_settings: need_new=True
        elif not type(playlist_settings[cls.PLUGIN_SETTINGS_FIELD_NAME]) is str: need_new=True
        if need_new:
            return cls.parse_plugin_settings( '' )
        
        return cls.parse_plugin_settings( playlist_settings[cls.PLUGIN_SETTINGS_FIELD_NAME] )
    
    @classmethod
    def _compress_plugin_settings( cls, plugin_settings ):
        
        # Converts given plugin settings into a
        # string that could be written to `db`.
        
        items = []
        for key, value in plugin_settings.items():
            item = f'{key}:{value}'
            items.append( item )
            
        return ';'.join(items)
    
    @classmethod
    def update_playlist_settings( cls, playlist_viewer, plugin_settings ):
        text = cls._compress_plugin_settings( plugin_settings )
        log.error( f'updating `playlist settings` from within `plugin` is not fully implemented yet, please add this data to `playlist settings` manually and reopen MainWindow / restart app (otherwise plugin settings will reset every time the playlist is opened): `{cls.PLUGIN_SETTINGS_FIELD_NAME}` = `{text}`' )
        
def remove_empty_folders():
    
    # I associate each playlist with one user-defined root folder.
    # Within this root folder FileRenamer can do lots of things.
    # Occaionally empty subfolders remain.
    # This function removes all empty subfolders in that root.
    
    root_folder = G_PLUGIN_SETTINGS[ ColumnsPluginSettings.root_folder ]
    
    if not os.path.isdir( root_folder ):
        log.error( f'invalid `root_folder`, can\'t clean it: {root_folder}' )
        return
    
    delete_empty_folders( root_folder )

def autoenable( grimoire_main_window, requester ):
    
    # remember
    global G_PLAYLIST_VIEWER
    global G_PLUGIN_INITIALIZED
    global G_PLUGIN_SETTINGS
    G_PLAYLIST_VIEWER = requester
    
    # get latest playlist viewer
    #playlist_viewer = g_grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if G_PLAYLIST_VIEWER is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, failed to enable' )
        return
    
    if G_PLUGIN_INITIALIZED:
        return
        
    # init settings
    G_PLUGIN_SETTINGS, did_change = ColumnsPluginSettings.get_plugin_settings( G_PLAYLIST_VIEWER.settings() )
    if did_change:
        ColumnsPluginSettings.update_playlist_settings( G_PLAYLIST_VIEWER, G_PLUGIN_SETTINGS )
    
    # mod context menu
    c = ColumnsActionDefinitions
    actions = [
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/remove_empty_folders',
            c.text: 'Remove empty folders',
            c.method: remove_empty_folders,
            },
        ]
    c.add_actions( G_PLAYLIST_VIEWER, actions )
    
    G_PLUGIN_INITIALIZED = True
    
def autodisable( grimoire_main_window, requester ):
    
    # remove modded actions
    
    if G_PLAYLIST_VIEWER is None:
        log.error( f'plugin {PLUGIN_NAME}, no valid playlist_viewer found, nothing to disable' )
        return
    
    # remove modded context menu
    c = ColumnsActionDefinitions
    act_identities = [
        f'grimoire/plugin/{PLUGIN_NAME}/remove_empty_folders'
        ]
    c.remove_actions( G_PLAYLIST_VIEWER, act_identities )
        
#---------------------------------------------------------------------------+++
# end 2023.10.21
# created
