# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Example custom main window.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
from PyQt5.QtWidgets import ( QTabWidget )
# same project
from sparkling.grimoire.pyqt5.PlaylistViewer import PlaylistViewer

class TabWidgetForPlaylistViewers( QTabWidget ):

    def __init__( self,
                  parent=None,
                  *args, **kwargs ):
        super( TabWidgetForPlaylistViewers, self ).__init__(
            parent=parent, *args, **kwargs )
        
        self.setContentsMargins(0,0,0,0)
        
        # signals
        
        self.tabBarClicked.connect( self.__focus_chosen_playlist_viewer )
        
    def __focus_chosen_playlist_viewer( self, iloc ):
        
        # get playlist viewer from this tab
        w = self.widget( iloc )
        
        # trigger focusInEvent
        w.setFocus()
        
    def get_playlist_viewer( self, p ):
        
        # Finds an existing PlaylistViewer that corresponds to
        # given playlist p.
        
        iloc = 0
        count = self.count()
        
        while iloc < count:
            
            w = self.widget(iloc)
            if type(w)==PlaylistViewer:
                # this is correct class
                
                if w._playlist.basename() == p.basename():
                    # found it
                    return w
                
            # wrong view, advane to next one
            iloc += 1
            
        # did not find it
        
    def addTab( self, widget, tab_title ):
        
        super( TabWidgetForPlaylistViewers, self ).addTab( widget, tab_title )
        self.__focus_chosen_playlist_viewer( self.count()-1 )
        
#---------------------------------------------------------------------------+++
# end 2023.05.25
# created
