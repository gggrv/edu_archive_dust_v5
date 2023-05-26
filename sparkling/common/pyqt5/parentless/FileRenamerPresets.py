# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
# pip install
# same project
from sparkling.common.PresetManager import PresetManager
    
class Columns:
    
    LABELS = 'labels'
    SCREEN_NAME = 'screen_name'
    DB_NAME = 'db_name'
    RULE = 'rule'
    DESCRIPTION = 'desc'
    
class FileRenamerPresets( PresetManager ):
    
    Columns = Columns
    
    def __init__( self, file_name ):
        
        super( FileRenamerPresets, self ).__init__( file_name )
        
    def get_presets( self ):
        
        # Returns saved presets.
        
        # load them as they are supposed to be
        super( FileRenamerPresets, self ).get_presets()
        
        # fix quotation marks around complex
        # "r''..[no,ok][if]" rules
        
        for k, v in self._presets.items():
            rule = v[Columns.RULE]
            if rule.startswith('"') and rule.endswith('"'):
                rule = rule[1:]
                rule = rule[:-1]
                self._presets[k][Columns.RULE] = rule
        
        return self._presets
        
    def new_preset(
            self,
            unique_name,
            labels,
            screen_name,
            db_name,
            rule,
            description
            ):
        
        # Saves preset.
        
        c = Columns
        
        # add new
        
        row = {
            c.LABELS: labels,
            c.SCREEN_NAME: screen_name,
            c.DB_NAME: db_name,
            c.RULE: rule,
            c.DESCRIPTION: description
            }
            
        if self._presets is None:
            # im creating first preset ever
            
            self._presets = {
                unique_name: row
                }
            
        else:
            # im adding new to some alreafy existing
            self._presets[unique_name] = row
            
        self._save_all_presets()

#---------------------------------------------------------------------------+++
# end 2023.05.11
# added
