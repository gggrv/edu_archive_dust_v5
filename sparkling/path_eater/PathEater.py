# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Creates queues for other widgets.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
# same project
from sparkling import MainPaths
from sparkling.common.DfEditor import DfEditor
from sparkling.neo4j.SpecialColumns import SpecialColumns as Sc

class Paths:
    
    JOB = 'path_eater'
    
    SAVE_LIST = MainPaths.set_job_output( JOB, 'queue.csv' )

class PathEater( QWidget ):
    
    OK_TO_CLOSE = pyqtSignal( str )
    
    class Strings:
        
        WINDOW_TITLE = 'Path Eater'
    
    paths = None
    
    editor = None

    def __init__( self,
                  paths=None,
                  parent=None,
                  *args, **kwargs ):
        super( PathEater, self ).__init__( parent, *args, **kwargs )
        
        self.setWindowTitle( PathEater.Strings.WINDOW_TITLE )
        
        self.paths = paths or []

        mock_entries = []
        for path in self.paths: mock_entries.append(
            {Sc.path:path}
            )

        self.editor = DfEditor(
            df=pd.DataFrame(mock_entries),
            parent=self,
            )

        # layout

        lyt = QVBoxLayout()
        lyt.setContentsMargins( 0,0,0,0 )

        lyt.addWidget( self.editor )
        self.setLayout( lyt )
        
        self.editor.OK_TO_CLOSE.connect( self.close )
        self.editor.EDITING_FINISHED.connect( self.editingFinishedEvent )
        
    def closeEvent( self, ev ):
        self.OK_TO_CLOSE.emit( self.objectName() )
        ev.ignore() # !!!
    
    def editingFinishedEvent( self, changes ):
        
        old_df, new_df = changes
        if len(new_df)==0: return
        
        src = Paths.SAVE_LIST
        
        if os.path.isfile( Paths.SAVE_LIST ):    
            prev_df = pd.read_csv( Paths.SAVE_LIST )
            prev_df = prev_df[ prev_df[Sc.path].isin( new_df[Sc.path] ) ]
            new_df = pd.concat( [prev_df,new_df], axis=0, sort=False )
            
        new_df.to_csv( src, index=False )
        
        self.editor.close()
        
#---------------------------------------------------------------------------+++
# end 2022.07.31
# redefined as separate job