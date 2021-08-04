# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2019-01-27 17:34:53
# @Last Modified by:   jose
# @Last Modified time: 2021-08-02 20:47:46

import os                       # os library
import argparse                 # argument parser

from registration import register_sequential_syn

def main():
    # Arguments details
    parser = argparse.ArgumentParser(description='Register sequentially all images in a folder. \
                        Sequence in alphabetical order. Registration with ANTS library')
    parser.add_argument("input_folder", type=str, 
                        help='Input folder with images')
    parser.add_argument("output_folder", type=str,
                        help='Output folder to store transformations')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent registrations')
    parser.add_argument('-o', '--one_way', action='store_true',
                        help='Enable sequential registration for fixed to moving only. \
                        The default behavior is to register fixed to moving and viceversa')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v','--verbose', action='store_true',
                        help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    one_way = args.one_way
    overwrite = args.overwrite

    # Files organized alphabetically
    files = os.listdir(input_folder)
    files.sort()
    print('\nRunning script to register 3d images sequentially.')
    if args.debug:
        print('[Debug Mode]')
    if args.verbose:    
        print('\nFiles found: \n' + str(files))
    print('\nRegistration\n')
    # os.system('export ANTSPATH=/usr/bin/')
    
    # List of files indexes. Added a zero (0) to complete the sequence
    idx = list(range(len(files)))
    idx.append(0)
    # print(idx)

    # Create directory to save output
    output_path = os.path.join(output_folder,'seq/')    # Output path
    os.system('echo mkdir -p ' + output_path )          # echo mkdir
    if not args.debug: 
        os.system('mkdir -p ' + output_path )           # make directory

    # Script loop
    for k in range(len(files)):
        # Register fixed to moving incrementally
        fixed_image = os.path.join(input_folder, files[idx[k]])      # Fixed image path
        moving_image = os.path.join(input_folder, files[idx[k+1]])   # Moving image path

        register_sequential_syn(fixed_image, moving_image, output_path, args.debug, overwrite)

        # Register now moving to fixed. Default behavior two ways (not one_way).
        if not one_way:
            register_sequential_syn(moving_image, fixed_image, output_path, args.debug, overwrite)

if __name__ == "__main__":
    # execute only if run as a script
    main()