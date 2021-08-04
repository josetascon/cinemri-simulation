# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2021-08-02 17:09:27
# @Last Modified by:   jose
# @Last Modified time: 2021-08-04 11:20:10

import os                       # os library, used to read files
import argparse                 # argument parser
import yaml                     # read parameters

from src.folder import listdir_fullpath

def main():
    # Arguments details
    parser = argparse.ArgumentParser(description='CineMRI simulation with underlined segmentations using preoperative images.')
    parser.add_argument("input_folder", type=str, 
                        help='Input folder with images. This folder must have 3 folders with images: 4dct, mr and rt (dicom rtstruct).')
    parser.add_argument("model_folder", type=str, 
                        help='Model folder with breathing model transformations.')
    parser.add_argument("output_folder", type=str,
                        help='Output folder to store CineMR image sequences with ground truth segmentations.')
    parser.add_argument("parameters", type=str,
                        help='File with video parameters.')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent registrations')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v','--verbose', action='store_true',
                        help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    folder_input = args.input_folder
    folder_model = args.model_folder
    folder_output = args.output_folder
    file_parameters = args.parameters
    overwrite = args.overwrite
    debug = args.debug
    verbose = args.verbose

    str_debug = '-d' if debug else '';
    str_write = '-w' if overwrite else '';

    # Parse noise parameters
    stream = open(file_parameters, 'r')
    params = yaml.safe_load(stream)

    noise_model     = None  # noise model
    noise_percent   = 0.1   # noise percentage

    if 'Video' in params:
        if 'noise-model' in params['Video']:
            noise_model = params['Video']['noise-model']
        if 'noise-percentage' in params['Video']:
            noise_percent = params['Video']['noise-percentage']

    # Folders and Files
    folder_4dct = os.path.join(folder_input, '4dct')
    folder_mr = os.path.join(folder_input, 'mr')
    folder_rt = os.path.join(folder_input, 'rt')

    files_4dct = listdir_fullpath(folder_4dct)
    file_4dct00 = files_4dct[0]
    file_mr = listdir_fullpath(folder_mr)[0]

    # Breathing model
    # - sequential registration
    # - 4dct00 to mri

    print('='*50 + '\n\t\tBreathing Model\n' + '='*50)
    cmd = 'python src/breathing-model-registration.py -o {} {} {}'.format(str_debug, 
        folder_4dct, folder_model)
    if verbose:
        print(cmd)
    os.system(cmd)
    print()

    cmd = 'python src/breathing-model-4dct00-mr.py {} {} {} {}'.format(str_debug, 
        file_4dct00, file_mr, folder_model)
    if verbose:
        print(cmd)
    os.system(cmd)
    print()


    # Video Simulation and Synthesis
    # - parse parameters
    print('='*50 + '\n\t\tVideo Simulation\n' + '='*50)

    cmd = 'python src/video-synthesis-simulation.py {} {} {} {} {} {}'.format(str_debug, 
        str_write, folder_input, folder_model, folder_output, file_parameters)
    if verbose:
        print(cmd)
    os.system(cmd)
    print()

    if noise_model != None:
        folder_ii = os.path.join(folder_output,'image')
        folder_oo = os.path.join(folder_output,'noise')

        cmd = 'python src/video-synthesis-noise.py -vr {} {} {} {} -t {} -s {}'.format(str_debug, 
            str_write, folder_ii, folder_oo, noise_model, noise_percent, noise_percent)
        if verbose:
            print(cmd)
        os.system(cmd)
        print()

if __name__ == "__main__":
    # execute only if run as a script
    main()