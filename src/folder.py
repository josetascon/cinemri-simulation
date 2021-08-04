# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2019-02-15 13:39:53
# @Last Modified by:   jose
# @Last Modified time: 2021-07-09 15:44:24

import os                           # os library, used to read files

def clean_file_name_and_format(file):
    '''
    Remove folder path of file. The filename is after the last /
    Check the last /
    Input: 
        file: string
    Output: 
        ref2: string
    '''

    # ref1 = file.split('/')
    # ref2 = ref1[-1]
    # return ref2

    base = os.path.basename(file)
    return base


def clean_file_name(file):
    '''
    Remove folder path and extension to file. The filename is between / and .
    Check the last . and /
    Input: 
        file: string
    Output: 
        ref2: string
    '''
    # ref1 = file.split('/')
    # ref2 = ref1[-1]
    # ref3 = ref2.split('.')
    # reff = ref3[0]
    # # print(reff)
    # return reff
    base = clean_file_name_and_format(file)
    return os.path.splitext(base)[0]

def clean_file_extension(file):
    '''
    Return file extension
    Input: 
        file: string
    Output: 
        string
    '''
    base = clean_file_name_and_format(file)
    return os.path.splitext(base)[-1][1:] # without the dot

def listdir_fullpath(d, sort = True):
    '''
    List a directory and return the file list with fullpath
    Input: 
        d: string
        sort: bool. Sort in alphabetical order
    Output: 
        listf: list of strings
    '''
    listf = [os.path.join(d, f) for f in os.listdir(d)]
    if sort: listf.sort()
    return listf

def listdir_fullpath_onlydir(d):
    '''
    List a directory and return only the directory list with fullpath
    Input: 
        d: string
    Output: 
        listf: list of strings
    '''
    files = listdir_fullpath(d, sort = True)
    return list(filter(os.path.isdir, files))

def listdir_fullpath_onlyfiles(d):
    '''
    List a directory and return only the files list with fullpath
    Input: 
        d: string
    Output: 
        listf: list of strings
    '''
    files = listdir_fullpath(d, sort = True)
    return list(filter(os.path.isfile, files))

def fullpath_to_localpath(files):
    '''
    Remove the fullpath of a list of files
    Input: 
        files: list of strings
    Output: 
        listf: list of strings
    '''
    return [os.path.split(f)[1] for f in files] #  os.path.split returns (head, tail). Only tail is desired

def fullpath_to_last2folders_path(files):
    '''
    Remove the fullpath of a list of files
    Input: 
        files: list of strings
    Output: 
        listf: list of strings
    '''
    # for f in files:

    return [f.split(os.sep)[-2] + os.sep + f.split(os.sep)[-1] for f in files] #  os.path.split returns (head, tail). Only tail is desired

def localpath_to_fullpath(path, files):
    '''
    Add a path to all the files in a list
    Input: 
        path: dir path
        files: list of strings
    Output: 
        listf: list of strings
    '''
    return [os.path.join(d,f) for f in files]

def filter_folders_prefix( prefixs, folder_list, remove=False ):
    '''
    Filter a list of files with a list of prefix
    Input: 
        prefixs: list of strings
        folder_list: list of strings
    Output: 
        listv: list of strings
    '''
    listv = []
    if not remove:
        for folder in folder_list:
            for prefix in prefixs:
                if prefix in folder:
                    listv.append(folder)
    else:
        for folder in folder_list:
            out = True
            for prefix in prefixs:
                if prefix in folder:
                    out = False
            if out: listv.append(folder)
    return listv