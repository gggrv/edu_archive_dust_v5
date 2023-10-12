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
    QPushButton, QListWidget, QLineEdit )
# same project
from sparkling.grimoire.GrimoireNeo4jColumns import Columns as ColumnsNeo4j
from sparkling.common.PresetManager import PresetManager
# widgets
from sparkling.common.pyqt5.CbxForPresetManager import CbxForPresetManager
    
class Columns:
    
    neo4j_labels = ColumnsNeo4j.neo4j_labels
    db_name = ColumnsNeo4j.db_name
    
    screen_name = 'screen_name'
    rule = 'rule'
    desc = 'desc'
    
class PresetFileRenamer( PresetManager ):
    
    Columns = Columns
    
    def __init__( self, file_name ):
        
        super( PresetFileRenamer, self ).__init__( file_name )

class ColumnsFileRenamerConstructor:
    
    presets_manager = 'presets_mgr'
    
    @staticmethod
    def validate_constructor_parameters( ps ):
        
        # In order to reduce number of human errors,
        # this function provides an option to
        # manually check `constructor parameters` 
        # and enforce corrections before
        # sending them to the `constructor`.
        
        # short name for convenience
        c = ColumnsFileRenamerConstructor
        
        if c.presets_manager in ps:
            if type( ps[c.presets_manager] ) is None:
                ps.remove( c.presets_manager )
               
class FileRenamer( QDialog ):
    
    # TODO
    # file renamer = custom playlist viewer?
    # custom playlist viewer template instance that is references
    # by relevant subclasses?

    OK_TO_CLOSE = pyqtSignal( str )
    EDITING_FINISHED = pyqtSignal( tuple, str )
    
    # TODO
    # get rid of local df copies,
    # reference current playlist selection view instead
    df = None # future df
    old_paths = None # future series
    
    db_name = None
    
    ColumnsConstructor = ColumnsFileRenamerConstructor
    
    class Gui:
        preset_selector = None
        rules_input = None
        output = None
        bt_ok = None
        bt_no = None

    def __init__( self,
                  constructor_parameters,
                  parent=None,
                  *args, **kwargs ):
        super( FileRenamer, self ).__init__(
            parent, *args, **kwargs )

        # short name for convenience
        c = ColumnsFileRenamerConstructor
        ps = constructor_parameters
        
        self.setWindowTitle( 'Rename files...' )
        
        # layout
        lyt = QVBoxLayout()

        # controls

        hbox = QHBoxLayout()

        self.Gui.preset_selector = CbxForPresetManager( parent=self )
            
        self.Gui.rules_input = QLineEdit( parent=self )

        self.Gui.bt_ok = QPushButton( parent=self )
        self.Gui.bt_ok.setText( 'Rename' )
        
        self.Gui.output = QListWidget( parent=self )
        
        hbox.addWidget( self.Gui.preset_selector )
        hbox.addWidget( self.Gui.rules_input )
        hbox.addWidget( self.Gui.bt_ok )

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
            
        self.Gui.preset_selector.currentTextChanged.connect( self._preset_changed_event )
        self.Gui.rules_input.textChanged.connect( self.__rule_edited_event )
        self.Gui.bt_ok.clicked.connect( self.apply_selected_renaming_rule )
        
        if c.presets_manager in ps:
            self.Gui.preset_selector.set_preset_manager( ps[c.presets_manager] )

    def closeEvent( self, ev ):
        self.destroy( True, True )
        ev.ignore() # !!!
        
    def _preset_changed_event( self, value ):
        
        # Whenever I select some preset via `preset selector`,
        # I want to load a renaming rule.
        
        # short name for convenience
        c = self.Gui.preset_selector.get_preset_columns()
        p = self.Gui.preset_selector.current_preset()
        
        self.Gui.rules_input.setText( p[c.rule] )

    def preview_rule( self, rule=None ):
        
        # Generates new paths and outputs them to the list_view.
        
        if rule is None:
            rule = self.Gui.rules_input.text()
        rule = rule.strip()
        
        self.Gui.output.clear()
        
        if self.df is None:
            return
        
        c = ColumnsNeo4j
        
        #rule = self.Gui.rules_input.text()
        new_paths = []
        try:
            
            for _, row in self.df.fillna('').iterrows():
                
                new_path = row[c.path]
                if not c.is_move_protected( row ):
                    new_path = os.path.normpath( eval(rule) ) # str -> expression -> str
                new_paths.append( new_path )
                
        except:
            new_paths = None
        
        if new_paths:
            self.Gui.output.addItems( new_paths )
            
    def __rule_edited_event( self, rule ):
        self.preview_rule( rule=rule )
        
    def change_items( self, df_to_add, identities_to_remove, db_name ):
        
        # For external use only.
        
        if not db_name is None:
            self.db_name = db_name
        
        if not df_to_add is None:
            
            need_to_add = len(df_to_add.index)>0
            
            if need_to_add:
                self.__add_df( df_to_add )            
            
        if not identities_to_remove is None:
            
            need_to_rem = len(identities_to_remove)>0 \
                and not self.df is None
                
            if need_to_rem:
                self.__remove_identities( identities_to_remove )
        
        self.preview_rule()
        
    def __add_df( self, df ):
        
        # I want to rename rows is this additional df as well.
        
        if self.df is None:
            # i have completely new
            self.df = df
            self.old_paths = df[ColumnsNeo4j.path].copy()
            return
        
        # i need to append existing
        self.df = self.df.append( df )
        self.old_paths = self.old_paths.append( df[ColumnsNeo4j.path] )
        
    def __remove_identities( self, identities ):
        
        # I no longer want to rename these rows.
        # I am 100% sure that these identities are in df.
            
        self.df = self.df[ ~self.df.index.isin(identities) ]
        self.old_paths = self.old_paths[ ~self.old_paths.index.isin(identities) ]

    def apply_selected_renaming_rule( self ):
        
        # Obtains new paths from the list_view
        # and attempts to rename files in source df.
        
        if self.df is None:
            return
        
        c = ColumnsNeo4j

        new_paths = []
        for iloc in range( self.Gui.output.count() ):
            new_paths.append( self.Gui.output.item(iloc).text() )
            
        if len(new_paths)==0: return
        
        if not len(new_paths) == len( self.df.index ):
            raise ValueError

        iloc = 0
        for loc, row in self.df.iterrows():
            src = row[c.path]
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
                self.df.loc[ loc,c.path ] = dst
            except:
                pass
            iloc+=1

        # emit two pd.Series
        new_paths_s = pd.Series( new_paths, name=c.path, index=self.old_paths.index )
        self.old_paths.name = c.path
        self.EDITING_FINISHED.emit( (self.old_paths,new_paths_s), self.db_name )
        self.close()
        
    def select_first_preset( self ):
        
        if self.Gui.preset_selector.count() > 0:
            self.Gui.preset_selector.setCurrentIndex( 0 )
            self._preset_changed_event( None )
    
#---------------------------------------------------------------------------+++
# end 2023.10.12
# update
