# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
import shutil
# pip install
import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import ( QDialog, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QListWidget, QLineEdit )
# same project
from sparkling.neo4j.Columns import Columns

class FileRenamer( QDialog ):

    OK_TO_CLOSE = pyqtSignal( str )
    EDITING_FINISHED = pyqtSignal( tuple )
    
    df = None
    old_df = None
    
    class Gui:
        rules_cbx = None
        rules_input = None
        output = None
    
    class Presets:
        # TODO
        # filter them by scope depending on data being renamed
        FileRenamer = None
    
    class Strings:
        
        WINDOW_TITLE = 'File renamer'
        APPLY = 'Rename'

    def __init__( self,
                  presets_mgr=None,
                  df=None,
                  parent=None,
                  *args, **kwargs ):
        super( FileRenamer, self ).__init__(
            parent, *args, **kwargs )

        self.df = pd.DataFrame() if df is None else df
        self.old_df = pd.DataFrame() if df is None else df.copy()
        self.Presets.FileRenamer = presets_mgr
        
        # layout
        lyt = QVBoxLayout()

        # controls

        hbox = QHBoxLayout()

        self.Gui.rules_cbx = QComboBox( parent=self )
        self.Gui.rules_input = QLineEdit( parent=self )

        bt_ok = QPushButton( parent=self )
        bt_ok.setObjectName( 'bt_ok' )

        self.Gui.output = QListWidget( parent=self )
        
        hbox.addWidget( self.Gui.rules_cbx )
        hbox.addWidget( self.Gui.rules_input )
        hbox.addWidget( bt_ok )

        # assemble
        
        lyt.addLayout( hbox )
        lyt.addWidget( self.Gui.output )
        self.setLayout( lyt )
        
        # autorun
        
        self.setWindowTitle( FileRenamer.Strings.WINDOW_TITLE )
        
        self.Gui.rules_cbx.currentTextChanged.connect( self.paste_rule )
        self.Gui.rules_input.textChanged.connect( self.preview_rule )
            
        bt_ok.setText( FileRenamer.Strings.APPLY )
        bt_ok.clicked.connect( self.rename )
        
        self.__populate_cbx()
            
    def paste_rule( self, rule_name ):
        
        # Pastes chosen preexisting rule to the inp_rules field.
        
        presets = self.Presets.FileRenamer.get_presets()
        c = self.Presets.FileRenamer.Columns
        
        for p in presets.values():
            if p[ c.SCREEN_NAME ] == rule_name:
                self.Gui.rules_input.setText( p[c.RULE] )

    def closeEvent( self, ev ):
        self.destroy( True, True )
        ev.ignore() # !!!

    def preview_rule( self, *args ):
        
        # Generated new paths and outputs them to the list_view.
        
        c = Columns
        
        self.Gui.output.clear()
        
        rule = self.Gui.rules_input.text()
        
        new_paths = []
        
        try:
            
            for _, row in self.df.fillna('').iterrows():
                new_path = os.path.normpath( eval(rule) ) # str -> expression -> str
                new_paths.append( new_path )
                
        except:
            new_paths = None
        
        if new_paths:
            self.Gui.output.addItems( new_paths )

    def rename( self ):
        
        # Obtains new paths from the list_view
        # and attempts to rename files in source df.
        
        c = Columns

        new_paths = []
        for iloc in range( self.Gui.output.count() ):
            new_paths.append( self.Gui.output.item(iloc).text() )
            
        if len(new_paths)==0: return
        
        if not len(new_paths) == len( self.df.index ):
            raise ValueError

        iloc = 0
        for loc, row in self.df.iterrows():
            src = row[c.PATH]
            dst = new_paths[iloc]
            new_catalogue = os.path.dirname( dst )

            if not os.path.exists(new_catalogue):
                os.makedirs( new_catalogue )
                
            if os.path.exists(dst):
                # skip - already exists
                iloc+=1
                continue
    
            try:
                shutil.move( src, dst )
                self.df.loc[ loc,c.PATH ] = dst
            except:
                pass
            iloc+=1

        self.EDITING_FINISHED.emit( (self.old_df,self.df) )
        self.close()
        
    def __populate_cbx( self ):
        
        # Is done once upon init.
        
        self.blockSignals( True )
        
        self.Gui.rules_cbx.clear()
        self.Gui.rules_input.clear()
        
        if self.Presets.FileRenamer is None:
            self.blockSignals( False )
            return
            
        # show some presets
        
        presets = self.Presets.FileRenamer.get_presets()
        c = self.Presets.FileRenamer.Columns
        
        screen_names = [ p[c.SCREEN_NAME] for p in presets.values() ]
        self.Gui.rules_cbx.addItems( screen_names )
    
        self.blockSignals( False )
        
        # trigger first rule
        if self.Gui.rules_cbx.count()>0:
            values = list( presets.values() )
            rule = values[0][ c.RULE ]
            self.Gui.rules_input.setText( rule )
    
#---------------------------------------------------------------------------+++
# end 2023.05.11
# simplified
