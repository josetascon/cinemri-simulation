# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2019-01-27 17:34:53
# @Last Modified by:   jose
# @Last Modified time: 2021-08-02 22:32:58

import os                       # os library
import argparse                 # argument parser

from registration import register_4dct00_mr

def main():
    # Arguments details
    parser = argparse.ArgumentParser(description='Register two images with SyN Ants')
    parser.add_argument("file_fixed", type=str, 
                        help='Input folder with images')
    parser.add_argument("file_moving", type=str,
                        help='Output folder to store transformations')
    parser.add_argument("output_folder", type=str,
                        help='Output folder to store transformations')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent registrations')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v','--verbose', action='store_true',
                        help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    file_fixed = args.file_fixed
    file_moving = args.file_moving
    folder_output = args.output_folder
    overwrite = args.overwrite
    debug = args.debug

    # Files organized alphabetically
    print('\nRunning script to register MR and 4DCT00.')
    if args.debug:
        print('[Debug Mode]')
    if args.verbose:    
        print('\nFiles: \n')
        print(file_fixed)
        print(file_moving)
    print('\nRegistration\n')
    # os.system('export ANTSPATH=/usr/bin/')
    
    # Create directory to save output
    output_path = os.path.join(folder_output,'4dct-mr/')    # Output path
    os.system('echo mkdir -p ' + output_path )          # echo mkdir
    if not args.debug: 
        os.system('mkdir -p ' + output_path )           # make directory

    # Script
    register_4dct00_mr(file_fixed, file_moving, output_path, debug, overwrite)


if __name__ == "__main__":
    # execute only if run as a script
    main()