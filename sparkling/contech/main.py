# -*- coding: utf-8 -*-
#BSD Zero Clause License
#
#Copyright (C) 2023 by Anna Anikina
#
#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted.
#
#THE SOFTWARE IS PROVIDED “AS IS” AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN
#AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#---------------------------------------------------------------------------+++

# logging
import logging
log = logging.getLogger(__name__)

# embedded in python
import os
import subprocess
# pip install
import pandas as pd
# same project
from sparkling.contech.StandardContextConventions import ConventionsStandard as Conventions
from sparkling.contech.StandardContextCommands import CommandsStandard as Commands
from sparkling.common import (
    readf, chop,
    select_files,
    replace_text_in_file,
    ColumnsFoundTexts, find_text_in_file )

class ColumnsFoundTags( ColumnsFoundTexts ):
    
    tag_name = 'tag'
    tag_value = 'value'
    
    product_root = 'product_root'
    project_root = 'project_root'
    
    texts = {
        tag_name: 'Tag name',
        tag_value: 'Tag value',
        product_root: 'Product root',
        project_root: 'Project root'
        }.update( ColumnsFoundTexts.texts )
    
def get_existing_environments( project_root, prefix=Conventions.ENVIRONMENT_NAME_PREFIX, dot_ext='.tex', relpath=False ):
    
    # Gets all existing env.tex in given project.
    
    # Depending on prefix, this function may mistake other
    # files as environments.
    
    if not os.path.isdir( project_root ):
        return []
    return select_files( project_root, prefix, dot_ext, True, relpath )

def get_existing_products( project_root, prefix=Conventions.PRODUCT_NAME_PREFIX, dot_ext='.tex', relpath=False ):
    
    # Gets all existing product.tex in given project.
    
    # Depending on prefix, this function may mistake other
    # files as products.
    
    if not os.path.isdir( project_root ):
        return []
    return select_files( project_root, prefix, dot_ext, True, relpath )

def get_existing_components( root_folder, this_is_project, prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex', relpath=False ):
    
    # Gets all existing component.tex in a given product / project.
    # `this_is_project`=True means `look for all the components you can find`,
    # `this_is_project`=False means `look only for components in this folder`.
    
    # Depending on prefix, this function may mistake other
    # files as components.
    
    if not os.path.isdir( root_folder ):
        return []
    
    return select_files( root_folder, prefix, dot_ext, this_is_project, relpath )

def get_referenced_componenets( product_src, return_paths=True ):

    # Gets all components.tex referenced in product.tex.
    # They may not actually exist on disk.
    # Prefixes don't matter.

    if not os.path.isfile(product_src):
        # no file, nothing to look for
        return []

    # obtain actual root folder
    prd_root = os.path.dirname( product_src )
    
    # parse product
    result = []
    c = Commands
    for line in readf( product_src, join_lines=False ):
        
        if not f'{c.component} ' in line:
            continue

        basename = chop( line, f'{c.component} ', None )
        if ' ' in basename: basename=chop(basename,None,' ')
        if '%' in basename: basename=chop(basename,None,'%')
        if '\n' in basename: basename=chop(basename,None,'\n')
            
        if return_paths:
            result.append( os.path.join( prd_root, f'{basename}.tex' ) )
        else:
            result.append( basename )

    return result

def get_unreferenced_components(
        product_src,
        prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex',
        return_referenced=False ):

    # Finds all unreferenced components in a product.

    if not os.path.isfile( product_src ):
        raise FileNotFoundError

    prd_root = os.path.dirname( product_src )

    existing = get_existing_components( prd_root, False, prefix=prefix, dot_ext=dot_ext )
    referenced = get_referenced_componenets( product_src, return_paths=True )

    result = []
    for f in existing:
        if not f in referenced:    
            result.append( f )

    if return_referenced:
        return result, referenced
    return result

def parse_component_tags( src, tags=None ):

    # Parses source file and returns dictionary with
    # found unencapsulated tags and their values.

    # Word `tag` describes 2 things:
    # - a `context` `command`
    # - a `context` `switch`
    # For now only `commands` are supported.

    if tags is None:
        # TODO
        # allow to get all tags that exist in file
        log.error( 'please provide specific tags, not doing anything' )
        return []

    TEXT = readf(src)
    TEXTLEN = len(TEXT)

    found = []

    c = ColumnsFoundTags
    for tag in tags:

        # how many times does this tag appear in text?
        # iterate each found
        iloc = 0
        for _ in range( TEXT.count( tag ) ):
            iloc = TEXT.find( tag, iloc )

            L = iloc+len(tag) # next char iloc
            # text ended, tag value doesn't exist
            if TEXTLEN<=L:
                PLACEHOLDER = {
                    c.file_src: src,
                    c.iloc: iloc,
                    c.tag_name: tag,
                    c.tag_value: pd.NA,
                    }
                found.append( PLACEHOLDER )

            next_char = TEXT[L]

            # i provided full command
            if next_char=='[':
                R = TEXT.find(']',L)
                value = TEXT[ L+1 : R ]
                PLACEHOLDER = {
                    c.file_src: src,
                    c.iloc: iloc,
                    c.tag_name: tag,
                    c.tag_value: value,
                    }
                found.append( PLACEHOLDER )

            # i provided full switch
            if next_char=='{':
                R = TEXT.find('}',L)
                value = TEXT[ L+1 : R ]
                PLACEHOLDER = {
                    c.file_src: src,
                    c.iloc: iloc,
                    c.tag_name: tag,
                    c.tag_value: value,
                    }
                found.append( PLACEHOLDER )

    return pd.DataFrame( found, columns=list(c.texts) )

def parse_product_tags(
        product_root, tags=None,
        skip_components=None,
        prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex' ):
    
    # It is possible that prd.tex contains tags as well.
    # I don't parse them - only underlying components.

    c = ColumnsFoundTags

    if tags is None:
        # TODO
        # allow to get all tags that exist in file
        log.error( 'please provide specific tags, not doing anything' )
        return pd.DataFrame( [], columns=list(c.texts) )
    
    # make sure i actually have components to parse
    components = get_existing_components( product_root, False, prefix=prefix, dot_ext=dot_ext )
    if len( components )==0:
        return pd.DataFrame( [], columns=list(c.texts) )
    
    dfs = []

    for src in components:
        basename = os.path.basename( src )
        name = basename.replace( prefix, '' ) if prefix is not None else basename
        if name in skip_components or basename in skip_components or src in skip_components:
            continue
        found = parse_component_tags( src, tags=tags )
        dfs.append( found )
        
    df = pd.concat( dfs, axis=0 )
    df.sort_values( [c.iloc,c.file_src], inplace=True )
    df.reset_index( drop=True, inplace=True )
    return df

def replace_in_product( product_root, replacements,
    prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex' ):

    components = get_existing_components( product_root, False, prefix=prefix, dot_ext=dot_ext )
    for src in components:
        replace_text_in_file( src, replacements, inplace=True )

def replace_in_project( project_root, replacements,
    product_prefix=Conventions.PRODUCT_NAME_PREFIX,
    component_prefix=Conventions.COMPONENT_NAME_PREFIX,
    product_dot_ext='.tex', component_dot_ext='.tex' ):

    prds = get_existing_products( project_root, prefix=product_prefix, dot_ext=product_dot_ext )
    for src in prds:
        prd_root = os.path.dirname( src )
        replace_in_product( prd_root, replacements, prefix=component_prefix, dot_ext=component_dot_ext )

def find_in_product( product_root, texts, prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex' ):

    cs = get_existing_components( product_root, False, prefix=prefix, dot_ext=dot_ext )
    if len(cs) == 0:
        return pd.DataFrame( [], columns=list(ColumnsFoundTags.texts) )
    
    dfs = []
    for component in cs:
        df = pd.DataFrame( find_text_in_file(component,texts), columns=list(ColumnsFoundTags.texts) )
        df[ColumnsFoundTags.product_root] = product_root
        dfs.append( df )

    return pd.concat( dfs, axis=0, sort=False )

def find_in_project( project_root, texts,
    product_prefix=Conventions.PRODUCT_NAME_PREFIX,
    component_prefix=Conventions.COMPONENT_NAME_PREFIX,
    product_dot_ext='.tex', component_dot_ext='.tex' ):

    prds = get_existing_products( project_root, prefix=product_prefix, dot_ext=product_dot_ext )
    if len(prds) == 0:
        return pd.DataFrame( [], columns=list(ColumnsFoundTags.texts) )
    
    dfs = []
    for prd_src in prds.values():
        prd_root = os.path.split( prd_src )[0]
        df = find_in_product( prd_root, texts )
        df[ColumnsFoundTags.project_root] = project_root
        dfs.append( df )

    return pd.concat( dfs, axis=0, sort=False )

def render_product( prd_src, context_console_command='context' ):
    
    # Renders chosen .tex file as if it was
    # a product.
    
    # I assume that `context` `folder with binaries` is added
    # to system `PATH`.
    
    prev_root = os.getcwd()
    prd_root, basename = os.path.split( prd_src )
    
    os.chdir( prd_root )
    subprocess.call( f'{context_console_command} {basename}' )
    os.chdir( prev_root )
    
    prd_name, _ = os.path.splitext(basename)
    
    return os.path.join( prd_root, f'{prd_name}.pdf' )

def get_references_definitions_for_product(
        product_root,
        tags=[Commands.reference],
        skip_components=None,
        prefix=Conventions.COMPONENT_NAME_PREFIX, dot_ext='.tex'
        ):

    # Parses given product (all existing components).
    # Generates references definitions for any
    # references found.
    
    # TODO:
    # allow user to specify custom reference
    # text for each known reference value

    # get tag values - who was referenced?
    df = parse_product_tags( product_root, tags=tags, skip_components=skip_components, prefix=prefix, dot_ext=dot_ext )
    found_references = df[ColumnsFoundTags.tag_value].unique()

    # generate valid .tex contents
    lines = []
    for reference in found_references:
        line = Commands.reference_with_value.replace('%value%',reference).replace('%text%',reference)
        lines.append(line)
        
    return lines
    
#---------------------------------------------------------------------------+++
# end 2023.10.14
# simplified
