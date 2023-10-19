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
from PyQt5.QtWidgets import ( QVBoxLayout, QComboBox,
    QDialog, QDialogButtonBox, QLineEdit )
# same project
from sparkling import MainPaths
from sparkling.contech.StandardContextProject import DStandardContextProject
from sparkling.contech.StandardContextCommands import CommandsStandard
from sparkling.common.pyqt5.ActionDefinitionsColumns import ColumnsActionDefinitions, BaseColumns
from sparkling.common import unique_loc
from sparkling.grimoire.PlaylistColumns import ColumnsPlaylist
from sparkling.common.enums.Consent import EConsent
from sparkling.contech.SomeContextProject import ColumnsProjectIndex

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
    PLUGIN_SETTINGS_FIELD_NAME = 'gp_nocontext'
    
    project_root = 'project_root'
    neo4j_labels = 'neo4j_labels'
    auto_show_rendered = 'auto_show_rendered'
    
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
                cls.project_root: project_root,
                cls.neo4j_labels: 'WrittenBook', # does not affect anything - i can manually set it to whatever
                cls.auto_show_rendered: EConsent.CONSENT,
                }, True
            
        # attempt to parse
        settings = {}
        
        for item in text.split(';'):
            
            key, value = item.split(':',maxsplit=1)
            settings[key] = value
            
            # force correct consent
            if key==cls.auto_show_rendered:
                if not value in [EConsent.CONSENT,EConsent.DECLINE]:
                    settings[key]=EConsent.CONSENT
            
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
        
        text = cls._compress_plugin_settings( plugin_settings )
        log.error( f'updating `playlist settings` from within `plugin` is not fully implemented yet, please add this data to `playlist settings` manually (otherwise plugin settings will reset every time the playlist is opened): `{cls.PLUGIN_SETTINGS_FIELD_NAME}` = `{text}`' )
        
        #new_settings = playlist_viewer.settings()
        #new_settings[cls.PLUGIN_SETTINGS_FIELD_NAME] = text

class Commands( CommandsStandard ):
    
    # define custom commands from the env_ here
    pass
    
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
        
        try:
            self.load_project_index()
        except FileNotFoundError:
            self.rebuild_project_index( save=True )
        
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
            
            # remember
            self.save_project_index()
            
            # send to db
            param_dict = {
                ColumnsPlaylist.path: prd_src,
                ColumnsPlaylist.title: f'Product for {unprefixed} (render me)',
                ColumnsPlaylist.album: unprefixed,
                ColumnsPlaylist.track_number: '1',
                ColumnsPlaylist.neo4j_labels: self.plugin_settings[ColumnsPluginSettings.neo4j_labels],
                }
            self.playlist_viewer._add_to_view_db( [param_dict], True )
            
    def new_component_in_product( self ):
        
        # Gui interface to `set_component_in_product`.
        
        # ask confirmation
        # help:
        # https://www.pythonguis.com/tutorials/pyqt-dialogs/
        # https://stackoverflow.com/questions/5760622/pyqt4-create-a-custom-dialog-that-returns-parameters
        
        if not ColumnsProjectIndex.PRODUCTS in self._project_index:
            log.error( 'no products found, please create at least 1 product in order to add components' )
            return
        
        dlg = QDialog()
        dlg.setWindowTitle( 'New component name?' )
        
        dlg.line = QLineEdit( parent=dlg )
        dlg.line.setText( '%s'%unique_loc() )
        
        dlg.prd_selector = QComboBox( parent=dlg )
        project_root = self.get_save_folder()
        for prd_src_rel in self._project_index[ColumnsProjectIndex.PRODUCTS]:
            prd_src = os.path.join( project_root, prd_src_rel )
            unpref, _ = self.Conventions.get_correct_product_names( prd_src, True )
            dlg.prd_selector.addItem( unpref, userData=prd_src )
        
        dlg.button_box = QDialogButtonBox( parent=dlg )
        dlg.button_box.setStandardButtons(
            QDialogButtonBox.Ok
            |QDialogButtonBox.Cancel
            )
        dlg.button_box.accepted.connect( dlg.accept )
        dlg.button_box.rejected.connect( dlg.reject )
        
        lyt = QVBoxLayout()
        lyt.addWidget( dlg.prd_selector )
        lyt.addWidget( dlg.line )
        lyt.addWidget( dlg.button_box )
        dlg.setLayout( lyt )
        
        if dlg.exec_():
            
            # create on disk
            
            c_name = dlg.line.text().strip()
            if c_name == '':
                log.error( 'component name must not be empty' )
                return
            prd_root = os.path.dirname( dlg.prd_selector.currentData() )
            unprefixed, prefixed = self.Conventions.get_correct_component_names( c_name, False )
            c_src = self.set_component_in_product( prd_root, unprefixed )
            
            # remember
            self.save_project_index()
            
            # send to db
            param_dict = {
                ColumnsPlaylist.path: c_src,
                ColumnsPlaylist.title: f'Component {unprefixed} (manually add me to product)',
                ColumnsPlaylist.album: self.Conventions.get_correct_product_names(prd_root,True)[0],
                ColumnsPlaylist.track_number: '2',
                ColumnsPlaylist.neo4j_labels: self.plugin_settings[ColumnsPluginSettings.neo4j_labels],
                }
            # TODO
            # fix neo4j_labels not working
            self.playlist_viewer._add_to_view_db( [param_dict], True )
    
    def render_selected( self ):
        
        # Renders only products.
        
        # obtain current selection
        df = self.playlist_viewer.selected_subdf()
        if len(df.index)==0:
            log.debug( 'nothing is selected, nothing to render' )
            return
        
        # foolcheck
        if not ColumnsProjectIndex.PRODUCTS in self._project_index:
            log.error( 'no products exist, nothing to render' )
            return
        elif len( self._project_index[ ColumnsProjectIndex.PRODUCTS ] ) ==0:
            log.error( 'no products exist, nothing to render' )
            return
        elif not ColumnsPlaylist.path in df.columns:
            log.error( 'selection can not be rendered' )
            return
        
        # obtain existing relative paths from index
        prds = self._project_index[ColumnsProjectIndex.PRODUCTS]
        #comps = self._project_index[ColumnsProjectIndex] if ColumnsProjectIndex.COMPONENTS in self._project_index else []
        # convert them to full paths
        project_root = self.get_save_folder()
        prds = [ os.path.join(project_root,p) for p in prds ]
        #comps = [ os.path.join(project_root,p) for p in comps ]
        
        # detect products that need to be rendered
        ok = []
        for path in df[ColumnsPlaylist.path]:
            if path in prds:
                ok.append( path )
        
        if len(ok) == 0:
            log.error( 'no products selected, nothing to render' )
            return
        
        for prd_src in ok:
            pdf_src = self.render_product( prd_src )    
            if self.plugin_settings[ColumnsPluginSettings.auto_show_rendered]:
                os.startfile( pdf_src )
    
def autoenable( grimoire_main_window, requester_playlist_viewer ):
    
    # make sure i have access to context project
    global G_BOOK
    if G_BOOK is None:
        G_BOOK = DWritingProject( requester_playlist_viewer )
    
    # mod context menu
    # TODO
    # add menu group rather then individual options
    # to reduce clutter
    c = ColumnsActionDefinitions
    actions = [
        {
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/new_product',
            c.text: 'New product',
            c.method: G_BOOK.new_product_in_project,
            },
        { # replaces new row
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/new_component',
            c.text: 'New component',
            c.method: G_BOOK.new_component_in_product,
            c.shortcut: 'Ctrl+N',
            },
        { # replaces print
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/render_product',
            c.text: 'Render selected products',
            c.method: G_BOOK.render_selected,
            c.shortcut: 'Ctrl+P',
            },
        { # TODO wrapper method that synchonizes nodes in `PlaylistViewer` with new `project index`
            c.identity: f'grimoire/plugin/{PLUGIN_NAME}/rescan_project',
            c.text: 'Rescan project',
            c.method: G_BOOK.rebuild_project_index,
            },
        ]
    c.add_actions( G_BOOK.playlist_viewer, actions )
        
def autodisable( grimoire_main_window, requester ):
    
    if G_BOOK is None:
        # plugin was not loaded at all
        return
    
    # remove modded actions
    
    c = ColumnsActionDefinitions
    act_identities = [
        f'grimoire/plugin/{PLUGIN_NAME}/new_product',
        f'grimoire/plugin/{PLUGIN_NAME}/new_component',
        f'grimoire/plugin/{PLUGIN_NAME}/render_product',
        ]
    c.remove_actions( G_BOOK.playlist_viewer, identities=act_identities )
        
#---------------------------------------------------------------------------+++
# end 2023.10.19
# update
