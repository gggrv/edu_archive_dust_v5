# -*- coding: utf-8 -*-
#Python utility "Tab Widget for Playlist Viewers". Allows to to organize "Grimoire Playlist Viewer"s into tabs. Copyright (C) 2023 Anna Anikina
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
# pip install
from PyQt5.QtWidgets import ( QTabWidget )
# same project
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer, ColumnsPlaylist

class TabWidgetForPlaylistViewers( QTabWidget ):

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( TabWidgetForPlaylistViewers, self ).__init__(
            parent=parent, *args, **kwargs )
        
        self.setContentsMargins(0,0,0,0)
        
        # make sure to connect tab closed signals externally
        self.setTabsClosable(True)
        
        # signals
                                                      
        # i want to trigger lots of code just by clicking the
        # tab name - otherwise my
        # code won't work until i click
        # the tab widget's inner area
        self.tabBarClicked.connect( self.__trigger_tab_focus_event )
        
    def __trigger_tab_focus_event( self, iloc ):
        
        # For internal use only.
        
        # get playlist viewer from this tab
        w = self.widget( iloc )
        
        # trigger focusInEvent
        w.setFocus()
        
    def get_playlist_viewer( self, settings ):
        
        # Finds an existing PlaylistViewer that corresponds to
        # playlist with given `settings`.
        
        c = ColumnsPlaylist
        
        # make sure i have means to compare
        # `settings`
        if not c.identity in settings:
            log.error( f'can\'t compare two NodeViewer `settings` because field `{c.identity}` is missing' )
            raise KeyError
        
        # iterate all
        iloc = 0
        count = self.count()
        while iloc < count:
            
            w = self.widget(iloc)
            if type(w)==PlaylistViewer:
                # this is correct class
                
                s = w.settings()
                if c.identity in s:
                    if s[c.identity] == settings[c.identity]:
                        # found it
            
                        # attept to update tab name
                        # if needed
                        if c.title in settings:
                            if not self.tabText( iloc ) == settings[c.title]:
                                self.setTabText( iloc, settings[c.title] )
                        
                        return w
                
            # wrong view, advance to the next one
            iloc += 1
            
        # did not find it
        
    def addTab( self, widget, tab_title ):
        
        super( TabWidgetForPlaylistViewers, self ).addTab( widget, tab_title )
        self.__trigger_tab_focus_event( self.count()-1 )
        
#---------------------------------------------------------------------------+++
# end 2023.10.06
# simplified
