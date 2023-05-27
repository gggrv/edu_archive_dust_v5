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
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import ( QDialog, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QListWidget, QLineEdit )
# same project
from sparkling.neo4j.Columns import Columns

class FileRenamer( QDialog ):

    OK_TO_CLOSE = pyqtSignal( str )
    EDITING_FINISHED = pyqtSignal( tuple )
    
    # TODO
    # get rid of local df copies,
    # reference current playlist selection view instead
    df = None # future df
    old_paths = None # future series
    
    class Gui:
        rules_cbx = None
        rules_input = None
        output = None
    
    class Presets:
        FileRenamer = None
    
    class Strings:
        
        WINDOW_TITLE = 'File renamer'
        APPLY = 'Rename'

    def __init__( self,
                  presets_mgr=None,
                  parent=None,
                  *args, **kwargs ):
        super( FileRenamer, self ).__init__(
            parent, *args, **kwargs )

        # dynamic
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
    
        # appearance
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            )
        self.Gui.output.setMinimumWidth( 1000 )
        
        # autorun
        
        self.setWindowTitle( FileRenamer.Strings.WINDOW_TITLE )
        
        self.Gui.rules_cbx.currentTextChanged.connect( self.paste_rule )
        self.Gui.rules_input.textChanged.connect( self.preview_rule )
            
        bt_ok.setText( FileRenamer.Strings.APPLY )
        bt_ok.clicked.connect( self.rename )
        
        self.__populate_cbx()
        
    def change_contents( self, add_df, remove_identities ):
        
        # For external use only.
        
        if not add_df is None:
            
            need_to_add = len(add_df.index)>0
            
            if need_to_add:
                self.__add_df( add_df )            
            
        if not remove_identities is None:
            
            need_to_rem = len(remove_identities)>0 \
                and not self.df is None
                
            if need_to_rem:
                self.__remove_identities( remove_identities )
        
        self.preview_rule()
        
    def __add_df( self, df ):
        
        # I want to rename rows is this additional df as well.
        
        if self.df is None:
            # i have completely new
            self.df = df
            self.old_paths = df[Columns.PATH].copy()
            return
        
        # i need to append existing
        self.df = self.df.append( df )
        self.old_paths = self.old_paths.append( df[Columns.PATH] )
        
    def __remove_identities( self, identities ):
        
        # I no longer want to rename those rows.
        # I am 100% sure that those identities are in df.
            
        self.df = self.df[ ~self.df.index.isin(identities) ]
        self.old_paths = self.old_paths[ ~self.old_paths.index.isin(identities) ]
        
    def paste_rule( self, rule_name ):
        
        # Pastes chosen preexisting rule to the inp_rules field.
        
        if self.Presets.FileRenamer is None:
            return
        
        presets = self.Presets.FileRenamer.get_presets()
        if len( presets )==0:
            return
        
        c = self.Presets.FileRenamer.Columns
        
        for p in presets.values():
            if p[ c.SCREEN_NAME ] == rule_name:
                self.Gui.rules_input.setText( p[c.RULE] )

    def closeEvent( self, ev ):
        self.destroy( True, True )
        ev.ignore() # !!!

    def preview_rule( self, *args ):
        
        # Generated new paths and outputs them to the list_view.
        
        if self.df is None:
            return
        
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
        
        if self.df is None:
            return
        
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

        # emit two pd.Series
        new_paths_s = pd.Series( new_paths, name=c.PATH, index=self.old_paths.index )
        self.old_paths.name = c.PATH
        self.EDITING_FINISHED.emit( (self.old_paths,new_paths_s) )
        self.close()
        
    def __populate_cbx( self ):
        
        # Is done once upon init.
        
        self.blockSignals( True )
        
        self.Gui.rules_cbx.clear()
        self.Gui.rules_input.clear()
        
        if self.Presets.FileRenamer is None:
            # no renamer, nohing to add
            self.blockSignals( False )
            return
            
        # show some presets
        
        presets = self.Presets.FileRenamer.get_presets()
        if len( presets ) is None:
            return
        
        # TODO
        # access current db, filter irrelevant rules
        
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
# end 2023.05.27
# fixed EDITING_FINISHED.emit
