# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------+++
# Tools for ConTeXt projects.

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
import subprocess
# pip install
import pandas as pd
# same project
from sparkling.contech.Conventions import Conventions
from sparkling.contech.Commands import Commands
from sparkling.common import (
    readf, savef, chop, select_files )

def get_components( product_root, prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex' ):

    # Gets all c_whatever.tex in product_root.
    # Returns { whatever: full_path_to_c_whatever.tex }.

    if not os.path.isdir( product_root ):
        raise FileNotFoundError

    components = select_files( product_root, prefix, dot_ext, True )

    table = {}

    for src in components:

        _,f = os.path.split(src)
        name,_ = os.path.splitext(f)
        
        if name.startswith( Conventions.COMPONENT_NAME_PREFIX ):    
            name = name.replace( Conventions.COMPONENT_NAME_PREFIX, '', 1 )

        table.setdefault( name, src )

    return table

def get_products( project_root, prefix=Conventions.PRODUCT_NAME_PREFIX, dot_ext='.tex' ):

    # Gets all prd_whatever.tex in project_root.
    # Returns { whatever: full_path_to_prd_whatever.tex }.

    if not os.path.isdir( project_root ):
        raise FileNotFoundError

    products = select_files( project_root, prefix, dot_ext, True )

    table = {}

    for src in products:

        _,f = os.path.split(src)
        name,_ = os.path.splitext(f)

        if name.startswith( Conventions.PRODUCT_NAME_PREFIX ):    
            name = name.replace( Conventions.PRODUCT_NAME_PREFIX, '', 1 )
            
        table.setdefault( name,src )

    return table

def get_referenced_componenets( product_src ):

    # Gets all c_whatever.tex referenced in prd_whatever.tex.
    # Returns { whatever: full_path_to_c_whatever.tex }.

    if not os.path.isfile(product_src):
        raise FileNotFoundError

    prd_root = os.path.dirname( product_src )
    table = {}

    for line in readf( product_src, join_lines=False ):
        
        if not f'\\component {Conventions.COMPONENT_NAME_PREFIX}' in line:
            continue

        name = chop( line, '\component ', None )
        if ' ' in name: name=chop(name,None,' ')
        if '%' in name: name=chop(name,None,'%')
        if '\n' in name: name=chop(name,None,'\n')

        if name.startswith( Conventions.COMPONENT_NAME_PREFIX ):    
            name = name.replace( Conventions.COMPONENT_NAME_PREFIX, '', 1 )
            
        src = os.path.join( prd_root, f'{name}.tex' )
        
        table.setdefault( name , src )

    return table

def get_unreferenced_components( product_src ):

    # Finds all unreferenced components in a product.

    if not os.path.isfile( product_src ):
        raise FileNotFoundError

    prd_root = os.path.dirname( product_src )

    existing = get_components(prd_root)
    referenced = get_referenced_componenets(product_src)

    table = {}

    for name in existing:
        if name in referenced:
            # it exists and it was referenced, everything ok
            continue
        table.setdefault( name, existing[name] )

    return table

def get_component_tags( src, tags=None ):

    # Parses source file and returns dictionary with
    # found unincapsulated tags and their values.

    # For now only commands are supported.

    if tags is None:
        # TODO
        # allow to get all tags that exist in file
        tags=[]

    TEXT = readf(src)
    TEXTLEN = len(TEXT)

    found = []

    for tag in tags:

        # how many times does this tag appear in text?
        # iterate each found
        iloc = 0
        for _ in range( TEXT.count( tag ) ):
            iloc = TEXT.find( tag, iloc )

            L = iloc+len(tag) # next char iloc
            # text ended, tag value doesnt exist
            if TEXTLEN<=L:
                PLACEHOLDER = {
                    'src': src,
                    'iloc': iloc,
                    'tag': tag,
                    'value': pd.NA,
                    }
                found.append( PLACEHOLDER )

            next_char = TEXT[L]

            # i provided full command
            if next_char=='[':
                R = TEXT.find(']',L)
                value = TEXT[ L+1 : R ]
                PLACEHOLDER = {
                    'src': src,
                    'iloc': iloc,
                    'tag': tag,
                    'value': value,
                    }
                found.append( PLACEHOLDER )

            # i provided full switch
            if next_char=='{':
                R = TEXT.find('}',L)
                value = TEXT[ L+1 : R ]
                PLACEHOLDER = {
                    'src': src,
                    'iloc': iloc,
                    'tag': tag,
                    'value': value,
                    }
                found.append( PLACEHOLDER )

    return pd.DataFrame( found, columns=['src','iloc','tag','value'] )

def get_product_tags( product_root, tags, skip_components ):

    components = get_components( product_root )

    dfs = []

    for name, src in components.items():
        if name in skip_components or src in skip_components:
            continue
        found = get_component_tags( src, tags )
        dfs.append( found )

    df = pd.concat( dfs, axis=0 )
    df.sort_values( ['iloc','src'], inplace=True )
    df.reset_index( drop=True, inplace=True )
    return df

def replace_in_file( src, replacements ):

    text = readf(src)
    changed_text = False

    for pair in replacements:

        if pair[0] in text:
            text = text.replace( pair[0],pair[1] )
            changed_text = True

    if changed_text:
        savef( src, text )

def replace_in_product( product_root, replacements ):

    components = get_components( product_root )
    for _, src in components.items():
        replace_in_file( src, replacements )

def replace_in_project( project_root, replacements ):

    prds = get_products( project_root )
    for src in prds.values():
        prd_root = os.path.dirname( src )
        replace_in_product( prd_root, replacements )

def find_in_file( src, texts ):

    # Parses source file and returns dictionary with
    # found things.

    TEXT = readf(src)

    found = []

    for text in texts:

        # how many times does this tag appear in text?
        # iterate each found
        iloc = 0
        for _ in range( TEXT.count( text ) ):
            iloc = TEXT.find( text, iloc )
            PLACEHOLDER = {
                'src': src,
                'iloc': iloc,
                'text': text,
                }
            found.append( PLACEHOLDER )

    return pd.DataFrame(found)

def find_in_product( product_root, texts ):

    dfs = []

    cs = get_components( product_root )
    for _, c_src in cs.items():
        df = find_in_file( c_src, texts )
        df['prd'] = product_root
        dfs.append( df )

    return pd.concat( dfs, axis=0, sort=False )

def find_in_project( project_root, texts ):

    dfs = []

    prds = get_products( project_root )
    for prd_src in prds.values():
        prd_root = os.path.split( prd_src )[0]
        df = find_in_product( prd_root, texts )
        df['project'] = project_root
        dfs.append( df )

    return pd.concat( dfs, axis=0, sort=False )

def render_product( prd_src, context_console_command='context' ):
    
    # Renders chosen .tex file as if it was
    # a product.
    
    prev_root = os.getcwd()
    prd_root, basename = os.path.split( prd_src )
    
    os.chdir( prd_root )
    subprocess.call( f'{context_console_command} {basename}' )
    os.chdir( prev_root )
    
    prd_name, _ = os.path.splitext(basename)
    
    return os.path.join( prd_root, f'{prd_name}.pdf' )

def get_references_definitions_for_product(
        product_root, tags=[Commands.REFERENCE2], skip_components=[]
        ):

    # Parses given product (all existing components).
    # Generates references definitions for any
    # references found.
    
    # TODO:
    # allow user to specify custom reference
    # text for each known reference value

    # get tag values - who was referenced?
    df = get_product_tags( product_root, tags, skip_components )
    found_references = df['value'].unique()

    # generate valid .tex contents
    lines = []
    for reference in found_references:
        line = Commands.REFERENCE.replace('%value%',reference).replace('%text%',reference)
        lines.append(line)
        
    return lines
    
#---------------------------------------------------------------------------+++
# end 2023.05.19
# added function for generating references definitions
