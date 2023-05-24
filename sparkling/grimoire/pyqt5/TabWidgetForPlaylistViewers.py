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
        
#---------------------------------------------------------------------------+++
# end 2023.05.25
# created
