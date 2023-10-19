# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QVBoxLayout,
    QDialog, QDialogButtonBox, QLineEdit )
# same project
from sparkling import MainPaths
from sparkling.contech.StandardContextProject import DStandardContextProject
from sparkling.contech.StandardContextCommands import CommandsStandard
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions, BaseColumns
from sparkling.common import unique_loc
from sparkling.grimoire.PlaylistColumns import ColumnsPlaylist

PLUGIN_NAME = 'nocontext'

# will hold the instance of the `DWritingProject`
G_BOOK = None

class ColumnsPluginSettings( BaseColumns ):
    
    # Plugin settings can be remembered in `db` as `node` `paremeter`
    # named `PLUGIN_SETTINGS_FIELD_NAME`.
    # TODO
    # validate contents so that neo4j never fails to
    # write this data to server
    
    # i will add this to playlist `settings` dict
    PLUGIN_SETTINGS_FIELD_NAME = f'gp_nocontext'
    
    project_root = 'project_root'
    
    # TODO
    # context root, text editor root, pdf viewer root
    
    @classmethod
    def parse_plugin_settings( cls, plugin_settings ):
        
        # short name for convenience
        text = plugin_settings
        
        did_change = False
        
        # force new
        if text == '':
            
            did_change = True
            
            # get correct project root
            project_root = os.path.join( MainPaths.data_root(), 'gp_nocontext%s'%unique_loc() )
            project_root = DWritingProject.Conventions.set_project( project_root )
            
            return {
                cls.project_root: project_root
                }
            
        # attempt to parse
        settings = {}
        for item in text.split(';'):
            key, value = item.split(':')
            settings[key] = value
        return settings, did_change
        
    @classmethod
    def get_plugin_settings( cls, playlist_settings ):
        
        # Will eithre parse/validate existing,
        # or create new ones from scratch.
        
        need_new = False
        if not cls.PLUGIN_SETTINGS_FIELD_NAME in playlist_settings: need_new=True
        elif not type(playlist_settings) is str: need_new=True
        if need_new:
            return cls.force_fix_plugin_settings( '' )
        
        return cls.parse_plugin_settings( playlist_settings[cls.PLUGIN_SETTINGS_FIELD_NAME] )
    
    @classmethod
    def _compress_plugin_settings( cls, plugin_settings ):
        
        # Converts given plugin settings into a
        # string that could be written to `db`.
        
        items = []
        for key, value in plugin_settings:
            item = f'{key}:{value}'
            items.append( item )
            
        return ';'.join(items)
    
    @classmethod
    def update_playlist_settings( cls, playlist_viewer, plugin_settings ):
        
        # `PlaylistViewer` settings can only be changed
        # via `PlaylistSelector`.
        
        # TODO
        # finish this method
        
        # also need to avoid update loops
        # (plugin -> playlist selector -> playlist viewer -> plugin -> ...)
        
        # plugins mod not just `playlist viewers`, but the whole
        # `grimoire` app, so having specific functions within
        # widgets `accept plugin settings` is pointless
        
        # instead of relying on gui `PlaylistSelector`,
        # it would be good to have 1 headless endpoint
        # that all relevant gui classes inherit/seek updates from
        # (in case i add multiple alternative `PlaylistSelectors`)
        
        text = cls.compress_plugin_settings( plugin_settings )
        log.error( f'updating `playlist settings` from within `plugin` is not fully implemented yet, please add this data to `playlist settings` manually (otherwise plugin settings will reset every time the playlist is opened): `{text}`' )
        
        #new_settings = playlist_viewer.settings()
        #new_settings[cls.PLUGIN_SETTINGS_FIELD_NAME] = text

class Commands( CommandsStandard ):
    
    # define custom commands from the env_ here
    pass
    
def open_note( src ):

    # make sure catalog exists
    root = os.path.dirname(src)
    if not os.path.exists(root):
        os.makedirs(root)

    # create blank file if it doesnt exist yet
    if not os.path.exists(src):
        savef( src,'' )

    os.startfile( src )
    
class DWritingProject( DStandardContextProject ):
    
    # A `plugin` version of the `standard context project` that is
    # suitable for professional writing.
    
    # will hold the reference to the plugin requester `QWidget`
    playlist_viewer = None
    
    # will hold parsed `playlist_viewer.settings()[FIELD_NAME]`
    plugin_settings = None

    def __init__( self, requester_playlist_viewer ):
        
        # remember
        self.playlist_viewer = requester_playlist_viewer
        self.plugin_settings, did_change = ColumnsPluginSettings.get_plugin_settings( self.playlist_viewer.settings() )
        
        if did_change:
            # write new `plugin settings` to `playlist settings` on `db`
            ColumnsPluginSettings.update_playlist_settings( self.playlist_viewer, self.plugin_settings )
        
        # init project
        super( DWritingProject, self ).__init__(
            self.plugin_settings[ColumnsPluginSettings.project_root],
            custom_conventions_class=None )
        
        # make sure necessary files exist
        self.set_project_in_project()
        self.set_environment_in_project()
        
    def new_product_in_project( self ):
        
        # Gui interface to `set_product_in_project`.
        
        # ask confirmation
        # help:
        # https://www.pythonguis.com/tutorials/pyqt-dialogs/
        # https://stackoverflow.com/questions/5760622/pyqt4-create-a-custom-dialog-that-returns-parameters
        
        dlg = QDialog()
        dlg.setWindowTitle( 'New product name?' )
        
        dlg.line = QLineEdit( parent=dlg )
        dlg.line.setText( '%s'%unique_loc() )
        
        dlg.button_box = QDialogButtonBox( parent=dlg )
        dlg.button_box.setStandardButtons(
            QDialogButtonBox.Ok
            |QDialogButtonBox.Cancel
            )
        dlg.button_box.accepted.connect( dlg.accept )
        dlg.button_box.rejected.connect( dlg.reject )
        
        lyt = QVBoxLayout()
        lyt.addWidget( dlg.line )
        lyt.addWidget( dlg.button_box )
        dlg.setLayout( lyt )
        
        if dlg.exec_():
            
            # create on disk
            prd_name = dlg.line.text().strip()
            if prd_name == '':
                log.error( 'product name must not be empty' )
                return
            unprefixed, prefixed = self.Conventions.get_correct_product_names( prd_name, False )
            prd_src = self.set_product_in_project( unprefixed )
            
            # send to db
            param_dict = {
                ColumnsPlaylist.path: prd_src,
                ColumnsPlaylist.title: f'Product for {unprefixed} (render me)',
                ColumnsPlaylist.album: unprefixed,
                }
            self.playlist_viewer._add_to_view_db( [param_dict], True )
        
        c = self.Conventions
        prd_src = c.set_product_in_project( self.get_save_folder(), product_name_unprefixed, custom_template=self._get_template(custom_template) )
        return super( DStandardContextProject, self )._set_product_in_project( prd_src )
    
def autoenable( grimoire_main_window, requester_playlist_viewer ):
    
    # make sure i have access to context project
    global G_BOOK
    if G_BOOK is None:
        G_BOOK = DWritingProject( requester_playlist_viewer )
    
    # mod context menu
    c = ColumnsActionDefinitions
    actions = [
        { # replaces new row
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/add_new_note',
            c.text: 'New note',
            c.method: G_BOOK.,
            c.shortcut: 'Ctrl+N',
            },
        { # replaces print
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/render_autoproduct',
            c.text: 'Render autoproducts for selected',
            c.method: MainDoer.render_autoproduct,
            c.shortcut: 'Ctrl+P',
            },
        # TODO
        # add `render selected as a new product
        # in a temp folder (if possible)`
        # rather then `render unique autoproducts for all selected`
        ]
    c.add_actions( requester, actions )
        
def autodisable( grimoire_main_window, requester ):
    
    if own_doer is None:
        # plugin was not loaded at all
        return
    elif own_doer.Doers.ProjectNotetaking is None:
        # plugin was partially not loaded, nothing to remove
        return
    
    # remove modded actions
    
    # get latest playlist viewer
    #playlist_viewer = own_doer.grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if requester is None:
        log.error( 'plugin notetaking, no valid playlist_viewer found, enable' )
        return
    
    # remove modded context menu
    c = ColumnsActionDefinitions
    modifications = [
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/add_new_note',
            c.remove:True },
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/render_autoproduct',
            c.remove:True },
        ]
    c.modify_actions( requester, modifications )
        
#---------------------------------------------------------------------------+++
# end 2023.10.13
# update
