# -*- coding: utf-8 -*-
#Python utility "Neo4J Tree View". Copyright (C) 2022 Anna Anikina
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