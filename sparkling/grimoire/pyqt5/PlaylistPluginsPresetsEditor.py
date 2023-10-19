# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QWidget, QGridLayout,
    QPushButton, QCheckBox, QLabel, QToolTip
    )
# same project
from sparkling.common import readf
from sparkling.grimoire.PlaylistPluginsPresets import PlaylistPluginsPresets
from sparkling.grimoire.PlaylistManager import (
    DEFAULT_PLAYLIST_SCREEN_NAME, DEFAULT_PLAYLIST_BASENAME
    )
        
class CustomCheckbox( QCheckBox ):
    
    # Custom Checkbox that emits not only current text,
    # but also some associated text that helps identify it.
    
    # Immediately shows tooltip.
    
    STATE_CHANGED = pyqtSignal( str, bool )

    def __init__( self,
                  text,
                  parent=None,
                  *args, **kwargs ):
        super( CustomCheckbox, self ).__init__( text, parent=parent, *args, **kwargs )
        
        self.stateChanged.connect( self.state_changed_event )
        
    def state_changed_event( self, new_state ):
        self.STATE_CHANGED.emit( self.text(), new_state )
    
    def mouseMoveEvent( self, ev ):
        
        # remove tooltip delay
        # help:
        # https://stackoverflow.com/questions/13720465/how-to-remove-the-time-delay-before-a-qtooltip-is-displayed
        # https://stackoverflow.com/questions/59914185/pyqt5-mouse-tracking-over-qlabel-object
        # https://stackoverflow.com/questions/31364809/pyside-instant-tooltips-no-delay-before-showing-the-tooltip
        
        QToolTip.showText(
            QCursor.pos(), #ev.pos(), # ev pos is relative to widget
            self.toolTip()
            )
        
        super( CustomCheckbox, self ).mouseMoveEvent( ev ) #hoverMoveEvent( ev )
        
class PlaylistPluginsPresetsEditor( QWidget ):
    
    # GUI editor for PlaylistPluginsPresets.
    
    REQUEST_PLUGIN_ENABLE = pyqtSignal( str )
    REQUEST_PLUGIN_DISABLE = pyqtSignal( str )
    
    class Folders:
        
        PLUGINS = None
    
    class Files:
        
        PLUGINS_PRESETS = None
        
        # each plugin may have this plain/rich text file
        # with description that will be shown in a tooltip
        PLUGIN_DESCRIPTION = 'desc'
        
    class Presets:
        
        PlaylistPlugins = None
        
    class Gui:
        
        info_lab = None
        bt_save = None
        
    # static
    __cached_existing_plugins = []
    
    # i manually update it from central widget
    # upon associated event
    # i expect it to always be up to date
    _basename = DEFAULT_PLAYLIST_BASENAME
        
    def __init__( self,
                  folder_with_plugins,
                  file_with_presets,
                  parent=None,
                  *args, **kwargs ):
        super( PlaylistPluginsPresetsEditor, self ).__init__( parent=parent, *args, **kwargs )

        # paths
        self.Folders.PLUGINS = folder_with_plugins
        self.Files.PLUGINS_PRESETS = file_with_presets

        # presets
        self.Presets.PlaylistPlugins = PlaylistPluginsPresets( self.Files.PLUGINS_PRESETS )
        
        # gui
        
        lyt = QGridLayout()
        
        self.Gui.info_lab = QLabel( DEFAULT_PLAYLIST_SCREEN_NAME, parent=self )
        self.Gui.bt_save = QPushButton( 'Save', parent=self )
        self.Gui.bt_save.clicked.connect( self.save_all_event )
        rowiloc = 0
        spanx = 2
        lyt.addWidget( self.Gui.info_lab, rowiloc,0, 1,spanx )
        lyt.addWidget( self.Gui.bt_save, rowiloc,spanx+1 )
        
        rowiloc = 2 # skip 1
        spanx = 2
        self.__cached_existing_plugins = os.listdir( self.Folders.PLUGINS )
        for plugin_name in self.__cached_existing_plugins:
            
            lab = CustomCheckbox( plugin_name, parent=self )
            lab.STATE_CHANGED.connect( self.checkbox_state_changed_event )
            
            # set description as tooltip if it exists
            desc_src = os.path.join( self.Folders.PLUGINS, plugin_name, PlaylistPluginsPresetsEditor.Files.PLUGIN_DESCRIPTION )
            if os.path.isfile( desc_src ):
                # add tooltip
                desc_text = readf( desc_src )
                lab.setToolTip( desc_text )
                lab.setMouseTracking( True ) # track only if tooltip
            
            #bt = QPushButton( '►', parent=self )
            #bt.setToolTip( 'Manually run.' )
            #bt.clicked.connect( self.manual_button_clicked_event )
            
            lyt.addWidget( lab, rowiloc,0, 1,spanx )
            #lyt.addWidget( bt, rowiloc,spanx+1, 1,1 )
            rowiloc += 1
        
        lyt.setRowStretch( lyt.rowCount(), 1 )
        self.setLayout( lyt )
        
    def save_all_event( self ):
        
        # Saves all currently checked plugin names
        # into presets.
        
        # iterate checkboxes,
        # get checked plugin names
        plugin_names = []
        for w in self.findChildren( QCheckBox ):
            plugin_name = w.text()
            is_plugin = plugin_name in self.__cached_existing_plugins # i have many checkboxes, make sure it holds plugin name
            if is_plugin and w.isChecked():
                # this is correct checkbox and
                # it is checked
                plugin_names.append( plugin_name )
        
        # save to disk
        self.Presets.PlaylistPlugins.save_preset(
            self._basename,
            plugin_names
            )
        
    #def manual_button_clicked_event( self, _ ):
    #    
    #    print()
        
    def checkbox_state_changed_event( self, plugin_name, new_state ):
        
        if new_state==Qt.Checked or new_state==True:
            # load
            self.REQUEST_PLUGIN_ENABLE.emit( plugin_name )
            return
        
        # don't unload, but reverse any changes
        # made to context menus, etc
        self.REQUEST_PLUGIN_DISABLE.emit( plugin_name )
        
    def set_current_active_playlist( self, p ):
        
        self.Gui.info_lab.setText( p.screen_name() )
        self._basename = p.basename()
        
        presets = self.Presets.PlaylistPlugins.presets()
        if not self._basename in presets:
            # uncheck all checkboxes
            for w in self.findChildren( QCheckBox ):
                plugin_name = w.text()
                is_plugin = plugin_name in self.__cached_existing_plugins # i have many checkboxes, make sure it holds plugin name
                if is_plugin and w.isChecked():
                    # this is correct checkbox
                    # make sure to uncheck it
                    w.setCheckState( Qt.Unchecked )
            # no need to do anything else
            return
        
        # short name for convenience
        preset = presets[self._basename]
        presets = None
        c = self.Presets.PlaylistPlugins.Columns
        
        for w in self.findChildren( QCheckBox ):
            plugin_name = w.text()
            is_plugin = plugin_name in self.__cached_existing_plugins # i have many checkboxes, make sure it holds plugin name
            if is_plugin:
                # this is correct checkbox
                if plugin_name in preset[c.ENABLED_PLUGINS]:
                    # i want this plugin to be enabled
                    if not w.isChecked():
                        # check this checkbox
                        w.setCheckState( Qt.Checked )
                else:
                    # i want this plugin to be disabled
                    if w.isChecked():
                        # uncheck
                        w.setCheckState( Qt.Unchecked )
        
#---------------------------------------------------------------------------+++
# end 2023.05.17
# created
