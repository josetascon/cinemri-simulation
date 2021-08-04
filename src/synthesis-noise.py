# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2020-10-10 11:26:42
# @Last Modified by:   jose
# @Last Modified time: 2021-08-04 10:48:00

import os
import argparse                 # argument parser
import numpy as np
import SimpleITK as sitk

from folder import *

def main():
    # Arguments descriptions
    parser = argparse.ArgumentParser(description='Add noise to a set of images')
    parser.add_argument("input_folder", type=str,
                        help='Input folder to create video')
    parser.add_argument("output_folder", type=str,
                        help='Output folder to store video')
    parser.add_argument('-t','--type', type=str, default='gaussian',
                        help='Noise types: gaussian (default), saltpepper, speckle, rician.')
    parser.add_argument('-s','--stddev', type=float, default=20.0,
                        help='Noise standard deviation')
    parser.add_argument('-r', '--percentage', action='store_true',
                        help='Noise as percentage')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent registrations')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v','--verbose', action='store_true',
                        help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    
    folder_input = args.input_folder
    folder_output = args.output_folder
    str_type = args.type
    stddev = args.stddev
    overwrite = args.overwrite
    percentage = args.percentage
    debug = args.debug
    verbose = args.verbose

    if verbose:
        print('\nInput Folder:\n', folder_input)

    list_files = listdir_fullpath_onlyfiles(folder_input)
    # if verbose:
    #     print('\nList of files:\n', fullpath_to_localpath(list_files))

    # verbose options
    options = ''
    if (percentage or overwrite or debug or verbose):
        options += '-'
    if (percentage):
        options += 'r'
    if (overwrite):
        options += 'w'
    if (debug):
        options += 'd'
    if (verbose):
        options += 'v'

    if verbose:
        print('\nOutput Folder:\n', folder_output)
    if not debug:
        os.makedirs(folder_output, exist_ok=True)

    list_out_files = listdir_fullpath(folder_output)

    if len(list_out_files) == len(list_files):
        print('\nExisting output noise files. Use option -w to overwrite')
        return 0

    ini = len(list_out_files)
    end = len(list_files)

    for k in range(ini,end):
        file = list_files[k]
        basename = fullpath_to_localpath([file])[0]
        file_output = os.path.join(folder_output, basename)
        
        cmd = 'python image-noise.py {} {} -t {} -s {} {}'.format(file, 
            file_output, str_type, stddev, options)
        if verbose:
            print(cmd)
        if not debug:
            os.system(cmd)
    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
