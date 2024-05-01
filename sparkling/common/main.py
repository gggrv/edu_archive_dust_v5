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
import datetime as dt
import os
import shutil
import zipfile
# pip install
import yaml
# same project
from sparkling.common.BaseColumns import BaseColumns
    
class ColumnsFoundTexts( BaseColumns ):
    
    file_src = 'src'
    iloc = 'iloc'
    text = 'text'
    
    texts = {
        file_src: 'Source file',
        iloc: 'Occurence number',
        text: 'Text',
        }
    
def generate_timestamp():
    return dt.datetime.now().strftime( '%Y.%m.%d %H:%M:%S' )

def unique_loc():
    return dt.datetime.now().strftime( '%Y%m%d%H%M%S' )

def delete_empty_folders( root_folder ):
    
    items = list( os.walk(root_folder) )
    
    for row in items[::-1]:
        root = row[0]
        subs = row[1]
        files = row[2]
        #print( root, len(subs)+len(files) )
        if len(subs)+len(files)==0:
            shutil.rmtree(root)
            #print('    rem')
            
def delrem( src ):
    
    if os.path.isfile(src):
        os.remove(src)
    elif os.path.isdir(src):
        shutil.rmtree(src)
            
def remove_forbidden_symbols( text, mode ):

    forbid = []

    if mode=='os':
        forbid = list(':?/\\*&|')

    for symbol in forbid: text=text.replace(symbol,'')

    return text

def count_lines( path ):
    
    # The fastest way to count number of lines
    # in the plaintext file.
    
    # help:
    # https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python/1019572#1019572
    
    return sum( 1 for _ in open(path) )

def readf( path, encoding='utf-8', n_lines=0, join_lines=True ):

    # Reads either the whole file or a specified number of lines from it.

    if n_lines>0:
        lines = []
        with open( path, 'r', encoding=encoding ) as f:
            for _ in range(n_lines):
                lines.append( f.readline() )
            log.info( 'read {n_lines} lines from file {file}'.format(n_lines=n_lines,file=path) )
            if join_lines: return '\n'.join(lines)
            else: return lines
    elif n_lines<0:
        with open( path, 'r', encoding=encoding ) as f:
            return f.readlines()

    with open( path, 'r', encoding=encoding ) as f:
        text = f.read()
        log.info( 'read file %s'%path )
        return text

def readf_yaml( path, encoding='utf-8' ):
    with open( path, 'r', encoding=encoding ) as f:
        data = yaml.safe_load(f)
        return data

def savef( path, text ):
    with open( path, 'w', encoding='utf-8' ) as f:
        f.write(text)
    log.info( 'saved file %s'%path )

def savef_yaml( path, data ):
    with open( path, 'w', encoding='utf-8' ) as f:
        yaml.dump( data, f )
    log.info( 'saved file %s'%path )

def appef( path, text ):
    with open( path, 'a', encoding='utf-8' ) as f:
        f.write(text)
    log.info( 'appended file %s'%path )

def chop( text, L, R ):
    A, B = 0, len(text)

    if type(L)==int: A=L
    elif type(L)==str: A=text.find(L)+len(L)
    text = text[A:]

    if type(R)==int: B=R
    elif type(R)==str: B=[B,text.find(R)][R in text]

    return text[:B].strip()

def find_text_in_file( src, texts ):

    # Parses source file and returns dictionary with
    # found things.

    TEXT = readf(src)

    c = ColumnsFoundTexts
    found = []
    for text in texts:

        # how many times does this tag appear in text?
        # iterate each found
        iloc = 0
        for _ in range( TEXT.count( text ) ):
            iloc = TEXT.find( text, iloc )
            PLACEHOLDER = {
                c.file_src: src,
                c.iloc: iloc,
                c.text: text,
                }
            found.append( PLACEHOLDER )

    return found

def replace_text_in_file( src, replacements, inplace=True ):
    
    # I expect replacements to be = [ ('old_value','new_value'), ... ].

    text = readf(src)
    changed_text = False

    for pair in replacements:

        if pair[0] in text:
            text = text.replace( pair[0],pair[1] )
            changed_text = True

    if changed_text:
        if inplace:
            savef( src, text )
        else:
            return text

def unzip( src, dest ):
    
    # Context-unaware function that unzips contents of
    # a source file in some destination folder.
    
    # help:
    # https://www.pythonpool.com/python-unzip/
    
    with zipfile.ZipFile( src ) as z:
        z.extractall( dest )
        
def extract_archives( archives, destination_folder, fail_folder ):
    
    if len( archives )==0: return # nothing to do
    
    # something to do
    
    failed_to_extract = []
    successfully_extracted = []
    
    # iterate files
    for src in archives:
            
        # i expect them all to be properly named
        if not src.endswith( '.zip' ):
            log.error( "it's not a .zip archive: {src}".format(src=src) )
            failed_to_extract.append( src )
        
        # actual unzipping
        try:
            unzip( src, destination_folder )
            successfully_extracted.append( src )
        except Exception as ex:
            # corrupted / wrong extension
            log.error( 'cant unzip file {src} because {ex}'.format(src=src,ex=ex) )
            failed_to_extract.append( src )
            
    # delete successfully extracted archives
    for src in successfully_extracted:
        # TODO possible error handling (most likely permissions)
        os.remove(src)
        
    # move failed archives
    if not fail_folder: return
    for src in failed_to_extract:
        dest = os.path.join( fail_folder, os.path.basename(src) )
        try:
            os.rename( src, dest )
        except Exception as ex:
            log.fatal( "can't move failed file {src} to {dest} because {ex}".format(src=src,dest=dest,ex=ex) )
        
def extract_all_archives( source_folder, destination_folder, fail_folder ):
    
    # This function extracts all archives in the source_folder
    # to some destination_folder.
    # If I was unable to extract the archive, I move it to the
    # fail_folder.
    
    if (fail_folder==source_folder) or fail_folder is None:
        fail_folder = None
    
    fs = os.listdir( source_folder )
    extract_archives( fs, destination_folder, fail_folder )

def remove_empty_folders( path_abs ):
    
    # function taken from here:
    # https://stackoverflow.com/questions/47093561/remove-empty-folders-python#comment118028859_64025990
    
    walk = list( os.walk(path_abs) )
    
    for path, _, _ in walk[::-1]:
        if len( os.listdir(path) ) == 0:
            shutil.rmtree(path)

def select_files( folder, prefix, dot_ext, check_subfolders, relpath, filter_function=None ):

    # Context-unaware file selection.

    selected = []

    for root, subs, fs in os.walk( folder, topdown=check_subfolders ):

        for f in fs:

            name,ext = os.path.splitext(f)
            if not name.startswith(prefix): continue
            if not ext==dot_ext: continue
        
            if not filter_function is None:
                if not filter_function( root, name, ext ):
                    continue

            src = os.path.join( root,f )
            if relpath:
                src = os.path.relpath( src, folder )
                
            selected.append(src)

    return selected

#---------------------------------------------------------------------------+++
# end 2023.10.14
# moved here some functions
