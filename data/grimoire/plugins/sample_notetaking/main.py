# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
#

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
# pip install
import pandas as pd
# same project
from sparkling.contech.Conventions import Conventions
from sparkling.contech.Commands import Commands as BaseCommands
from sparkling.contech.main import (
    get_references_definitions_for_product, render_product )
from sparkling.common.SomeDoer import SomeDoer
from sparkling.common import savef, select_files, readf
from sparkling.common.pyqt5.main import append_actions
from sparkling.neo4j.Columns import Columns as Neo4jColumns

own_doer = None

class Commands( BaseCommands ):
    
    # define custom commands from the env_ here
    pass
    
def open_note( src ):

    # make sure catalog exists
    root = os.path.dirname(src)
    if not os.path.exists(root):
        os.makedirs(root)

    # create blank file if it doesnt exist yet
    if not os.path.exists(src):
        savef( src,'' )

    os.startfile( src )
    
def generate_titles_tex( product_root ):

    # Parses given product (all existing components).
    # Generates a component named c_titles.tex
    # that contains all references mentioned in the product.
    # After including c_titles.tex in the prd_.tex,
    # and rendering .pdf, the references will display
    # human-readable text instead of `??`.

    # get definitions
    tags = [
        Commands.REFERENCE2,
        ]
    skip = [
        NoteTakingProject.Files.TITLES
        ]
    definitions = get_references_definitions_for_product( product_root, tags=tags, skip_components=skip, prefix='' )

    # generate valid .tex contents
    lines = [
        Commands.STARTCOMPONENT.replace( '%component_name%', NoteTakingProject.Files.TITLES )
        ]
    lines.extend( definitions )
    lines.append( Commands.STOPCOMPONENT )

    # save to disk
    src = os.path.join( product_root, f'{NoteTakingProject.Files.TITLES}.tex' )
    text = '\n'.join(lines)
    savef( src, text )
    
class NoteTakingProject( SomeDoer ):
    
    # Custom context project manager
    # specifically adapted for desktop note-taking.
        
    generate_titles_tex = staticmethod( generate_titles_tex )
    open_note = staticmethod( open_note )
    
    __project_name = None
    
    _products = None
        
    class Files:
        
        # custom auto-generated component that contains
        # definitions for all references mentioned
        # within this product.
        TITLES = 'c_titles'
        
        # this file should contain a single line of text
        # with full path to exsting context project
        # that is compatible with this plugin
        PRIVATE_PROJECT_ROOT = 'project_root'
        
    def __init__( self, save_folder ):
        
        # i expect `save_folder` to be blablabla/Conventions.PROJECT_NAME_PREFIXraw_name
        project_name = os.path.basename( save_folder )
        if not Conventions.PROJECT_NAME_PREFIX in project_name:
            raise NameError( f'please include {Conventions.PROJECT_NAME_PREFIX} in the project directory name' )
            
        super( NoteTakingProject, self ).__init__( save_folder )
        
        self.__project_name = os.path.basename( save_folder )
        
        # dynamic
        self._products = {}
        
    def project_name( self ):
        return self.__project_name
    
    def _get_product_definition( self, product_root ):
        
        # Combines all existing components into a product.
        
        # path structure:
        # ........product_root/YYYYMMDD_HHMMSS.tex
        # project_root/YYYY/MM/YYYYMMDD_HHMMSS.tex
        src, month = os.path.split(product_root)
        _, year = os.path.split(src)
        del src
        
        prd_name = f'{year}{month}'
        prd_src = os.path.join( product_root, f'prd_{prd_name}.tex' )
        raw_project_name = self.__project_name.replace( Conventions.PROJECT_NAME_PREFIX, '' )
            
        # generate reference titles
        generate_titles_tex( product_root )
        
        # generate valid .tex contents
        
        lines = [
            
            Commands.STARTPRODUCT.replace( '%product_name%' ,prd_name ),
            Commands.PROJECT.replace( '%project_name%', self.__project_name ),
            Commands.ENVIRONMENT.replace( '%environment_name%', f'env_{raw_project_name}' ),
            
            ]
        
        # write the import for each component
        component_srcs = select_files( product_root, f'{year}{month}', '.tex', False )
        for c_src in component_srcs:
            c_basename = os.path.basename(c_src)
            c_name, _ = os.path.splitext(c_basename)
            lines.append(
                Commands.COMPONENT.replace( '%component_name%', c_name )
                )
        del component_srcs
        
        # finish up
        lines.append( Commands.COMPONENT.replace( '%component_name%', NoteTakingProject.Files.TITLES ) )
        lines.append( Commands.STOPPRODUCT )
        
        # save to disk
        product_text = '\n'.join(lines)
        savef( prd_src, product_text )
        
        return prd_src
    
    def render_autoproduct( self, prd_root, show_result=False ):
        
        # Automatically creates and renders product.
            
        try:
            
            prd_src = self._get_product_definition( prd_root )
            result_flie = render_product( prd_src )
            
            if show_result:
                os.startfile( result_flie )
            else:
                return result_flie
            
        except FileNotFoundError:
            log.error( f'folder does not exis, cannot render product: {prd_root}' )
    
class MainDoer( SomeDoer ):
    
    grimoire_main_window = None

    class Folders:
        
        # full path to this plugin
        THIS_PLUGIN = os.path.dirname( __file__ )
        
        # where the context project if located
        CONTEXT_PROJECT_ROOT = None
    
    class Files:
        
        # this file will contain the path to the project
        CONTEXT_PROJECT_ROOT = 'project_root'
    
    class Strings:
        
        NEW_NOTE = 'New note'
        RENDER = 'Render autoproducts for selected'
        
    class Doers:
        
        ProjectNotetaking = None
    
    # this plugin dir name
    PREFERRED_SAVE_DIR_NAME = os.path.basename( Folders.THIS_PLUGIN )
    
    def __init__( self, grimoire_main_window ):
        super( MainDoer, self ).__init__( MainDoer.Folders.THIS_PLUGIN )

        self.grimoire_main_window = grimoire_main_window
        
        self.Files.CONTEXT_PROJECT_ROOT = self.set_file( self.Files.CONTEXT_PROJECT_ROOT )
        
        # read custom context project root from file
        
        if os.path.isfile( self.Files.CONTEXT_PROJECT_ROOT ):
            # path to context project exists
            
            self.Folders.CONTEXT_PROJECT_ROOT = readf( self.Files.CONTEXT_PROJECT_ROOT ).strip()
            
            if self.Folders.CONTEXT_PROJECT_ROOT.startswith( '.'+os.path.sep ):
                # make relative path into full
                self.Folders.CONTEXT_PROJECT_ROOT \
                    = MainDoer.Folders.THIS_PLUGIN \
                    + self.Folders.CONTEXT_PROJECT_ROOT[1:]
                    
        else:
            # path to context project does not exist
            # prompt user
            savef( self.Files.CONTEXT_PROJECT_ROOT, 'PASTE HERE FULL PATH TO EXISTING CONTEXT PROJECT' )
            os.startfile( self.Files.CONTEXT_PROJECT_ROOT )
        
    def _create_interface_to_project( self ):
    
        if not self.Doers.ProjectNotetaking is None:
            return True
        
        try:
            self.Doers.ProjectNotetaking = NoteTakingProject( self.Folders.CONTEXT_PROJECT_ROOT )
        except FileNotFoundError:
            # no access to context project root
            log.error( 'no access to context project root, can\'t enable plugin notetaking' )
        finally:
            return not self.Doers.ProjectNotetaking is None
        
    def render_autoproduct( *args ):
        
        # Renders automatically created products
        # for selected components.
        
        self = own_doer
        
        if self.Doers.ProjectNotetaking is None:
            return
        
        # short name for convenience
        c = Neo4jColumns
        
        # get latest playlist viewer
        playlist_viewer = self.grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
        if playlist_viewer is None:
            log.error( 'plugin notetaking, no valid playlist_viewer found' )
            return
        
        df = playlist_viewer.selected_subdf()
        if not c.path in df.columns: return
        
        # obtain unique roots
        # of all the products i want to render
        mask = df[c.path].str.contains('.tex') & ( df[c.path].notna() )
        c_srcs = df[mask][c.path]
        prd_roots = []
        for c_src in c_srcs:
            prd_root = os.path.dirname(c_src)
            if not prd_root in prd_roots:
                prd_roots.append( prd_root )
            
        # create the product
        for prd_root in prd_roots:
            self.Doers.ProjectNotetaking.render_autoproduct( prd_root, show_result=True )
    
    def new_note( *args ):
        
        # Use this instead of the NoteTakingProject one.
        
        self = own_doer
        
        if self.Doers.ProjectNotetaking is None:
            return
        
        # get latest playlist viewer
        playlist_viewer = self.grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
        if playlist_viewer is None:
            log.error( 'plugin notetaking, no valid playlist_viewer found, can\'t create new note' )
            return
        
        now = pd.Timestamp.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        date_human = now.strftime('%Y.%m.%d %X')
        date_path = now.strftime('%Y%m%d_%H%M%S')
        
        basename = f'{date_path}.tex'
        src = os.path.join( self.Folders.CONTEXT_PROJECT_ROOT, year, month, basename )
        
        # send to db, view
        metadata = {
            'timestamp': date_human,
            'year': year, #date_path[:4],
            'month': month, #date_path[4:6],
            Neo4jColumns.path: src,
            Neo4jColumns._NEO4J_LABELS: 'Note'
            }
        
        playlist_viewer._accept_custom_metadata( metadata )
        
        # launch external editor
        self.Doers.ProjectNotetaking.open_note( src )
    
def autoenable( grimoire_main_window ):
    
    # make sure i have doer
    global own_doer
    if own_doer is None:
        # create one
        own_doer = MainDoer( grimoire_main_window )
        
    # make sure it has access to project
    if own_doer.Doers.ProjectNotetaking is None:
        success = MainDoer._create_interface_to_project( MainDoer )
        
        if not success:
            # no point in doing anything else
            return
    
    # get latest playlist viewer
    playlist_viewer = own_doer.grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( 'plugin notetaking, no valid playlist_viewer found, enable' )
        return
        
    # mod context menu
    actions = [
        { # replaces new row
            'text': MainDoer.Strings.NEW_NOTE,
            'method': MainDoer.new_note,
            'shortcut': 'Ctrl+N',
            'owner': MainDoer.PREFERRED_SAVE_DIR_NAME
            },
        {
            'text': MainDoer.Strings.RENDER,
            'method': MainDoer.render_autoproduct,
            'shortcut': 'Ctrl+P',
            'owner': MainDoer.PREFERRED_SAVE_DIR_NAME
            },
        # TODO
        # add `render selected as a new product`
        # rather then `render unique autoproducts for all selected`
        ]
    
    append_actions( playlist_viewer, actions )
    
def autodisable( grimoire_main_window ):
    
    if own_doer is None:
        # plugin was not loaded at all
        return
    elif own_doer.Doers.ProjectNotetaking is None:
        # plugin was partially not loaded, nothing to remove
        return
    
    # remove modded actions
    
    # get latest playlist viewer
    playlist_viewer = own_doer.grimoire_main_window.centralWidget().Gui.tab_widget.currentWidget()
    if playlist_viewer is None:
        log.error( 'plugin notetaking, no valid playlist_viewer found, enable' )
        return
    
    # iterate through available actions
    for act in playlist_viewer.actions():
        
        try:
        
            # check custom owner parameter to see if
            # the action is created by a plugin
            # TODO
            # subclass QAction??
            if act._owner == MainDoer.PREFERRED_SAVE_DIR_NAME:
                playlist_viewer.removeAction( act )
                
        except AttributeError:
            
            # this action does not have custom owner parameter
            # this miens that it was not
            # created by any sort of plugin
            pass
        
#---------------------------------------------------------------------------+++
# end 2023.05.22
# ok basic clean version
