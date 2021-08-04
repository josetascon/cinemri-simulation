# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2020-10-10 11:26:42
# @Last Modified by:   jose
# @Last Modified time: 2021-08-04 10:48:46

import os
import sys
import argparse                 # argument parser
import yaml
import numpy as np
import SimpleITK as sitk

from folder import *
from image import *
from video import *

def main():
    # Arguments descriptions
    parser = argparse.ArgumentParser(description='Create CineMR simulation videos using 4DCT scans')
    parser.add_argument("input_folder", type=str, 
                        help='Input folder with images')
    parser.add_argument("model_folder", type=str, 
                        help='Model folder with transformations')
    parser.add_argument("output_folder", type=str,
                        help='Output folder to store transformations')
    parser.add_argument("parameters", type=str,
                        help='File with parameters')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent videos')
    parser.add_argument('-p','--plot', action='store_true',
                        help='Enable plot of reference')
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
    plot = args.plot

    # Default Parameters
    view            = 'sagittal'
    slice_num       = 180   # view slice value
    video_time      = 20.0  # video desired total time
    frame_per_sec   = 4     # video frames per second
    ref_phase       = 0     # reference phase in 4dct
    phases          = 10    # num phases 4dct
    breathing_time  = 4.5   # breathing cycle time in seconds
    amplitude       = 1.0   # amplitude of breathing
    # noise_model     = None  # noise model
    # noise_percent   = 0.1   # noise percentage
    random_amp      = False # amplitude with random value from 1.0 to 2.0

    labels_segments = []
    labels_names    = []

    # Parse parameters
    stream = open(file_parameters, 'r')
    params = yaml.safe_load(stream)

    if 'Video' in params:
        if 'camera-view' in params['Video']:
            view = params['Video']['camera-view']
        if 'slice' in params['Video']:
            slice_num = params['Video']['slice']
        if 'video-time' in params['Video']:
            video_time = params['Video']['video-time']
        if 'frame-per-second' in params['Video']:
            frame_per_sec = params['Video']['frame-per-second']
        if 'reference-phase' in params['Video']:
            ref_phase = params['Video']['reference-phase']
        if 'breathing-amplitude-type' in params['Video']:
            random_amp = True if params['Video']['breathing-amplitude-type'] == 'random' else False
        if 'breathing-amplitude' in params['Video']:
            amplitude = params['Video']['breathing-amplitude']
        if 'breathing-cycle-time' in params['Video']:
            breathing_time = params['Video']['breathing-cycle-time']
        if 'noise-model' in params['Video']:
            noise_model = params['Video']['noise-model']
        if 'noise-percentage' in params['Video']:
            noise_percent = params['Video']['noise-percentage']
    if 'Segments' in params:
        if 'labels-input' in params['Segments']:
            labels_segments = params['Segments']['labels-input']
        if 'labels-output' in params['Segments']:
            labels_names = params['Segments']['labels-output']
    
    # Folders and Files
    folder_4dct = os.path.join(folder_input, '4dct')
    folder_mr = os.path.join(folder_input, 'mr')
    folder_rt = os.path.join(folder_input, 'rt')

    files_4dct = listdir_fullpath(folder_4dct)
    file_4dct00 = files_4dct[0]
    file_mr = listdir_fullpath(folder_mr)[0]
    file_rt = listdir_fullpath(folder_rt)[0]
    
    file_reference = os.path.join(folder_model,'4dct-mr','4dct00_to_mr_Warped.nii.gz')
    folder_trfm = os.path.join(folder_model,'seq/')

    folder_out = os.path.join(folder_output, 'image/')
    if not debug:
        os.makedirs(folder_out, exist_ok=True)
    
    # Check if existing files in output
    existing_files = listdir_fullpath(folder_out)
    num_files = len(existing_files)
    ts = 1/frame_per_sec
    time = np.arange(0.0,video_time,ts)

    if (num_files) == len(time):
        print('[Warning] Existing CineMR files, use option -w to overwrite')
        return 0

    # Reference Image (mr in 4dct space)
    image_reference = sitk.ReadImage(file_reference, sitk.sitkFloat32)
    if verbose:
        print(image_info(image_reference,'Reference 3D, MR Image Information'))

    # Read transform 4dct-mr
    image_ct =  sitk.ReadImage(file_4dct00, sitk.sitkFloat32)
    file_affine = os.path.join(folder_model, '4dct-mr', '4dct00_to_mr_0GenericAffine.mat')
    file_dfield = os.path.join(folder_model, '4dct-mr', '4dct00_to_mr_1Warp.nii.gz')
    trfm_mr2ct = read_compose_transform(file_dfield, file_affine)

    # Dicom RS. Masks on mr and colors
    image_mr = sitk.ReadImage(file_mr, sitk.sitkFloat32)
    list_masks, list_colors = extract_image_masks(image_mr, file_rt, labels_segments, verbose)
    
    list_trfm_masks = [] # backwards for liver not to cover gtv
    for mask in list_masks:
        m = transform_image(mask, image_ct, trfm_mr2ct)
        list_trfm_masks.append(m)

    list_trfm_masks.reverse()

    # Plot slice
    if (plot):
        img2d = image3d_to_slice(image_reference, slice_num, view)
        img2d_label = img2d
        for i,mask in enumerate(list_trfm_masks):
            label_2d = image3d_to_slice(mask, slice_num, view)
            img2d_label = label_overlay(img2d_label, label_2d, list_colors[i])
        plt.figure()
        plt.subplot(1,2,1)
        imshow_2d(img2d, show=False)
        plt.subplot(1,2,2)
        imshow_2d(img2d_label, show=False)
        plt.show()

    # Reverse order, first gtv and then liver
    list_trfm_masks.reverse()

    # 4DCT transformations    
    files_trfms = listdir_fullpath(folder_trfm) # print(files)
    files_trfms_warp = filter_folders_prefix(['0Warp.'], files_trfms)
    files_trfms_inv_warp = filter_folders_prefix(['0InverseWarp.'], files_trfms)
    if verbose:
        print('\nWarp transform files: \n', fullpath_to_localpath(files_trfms_warp))
        print('\nInverse warp transform files: \n', fullpath_to_localpath(files_trfms_inv_warp))
    files_transforms = files_trfms_warp + files_trfms_inv_warp

    # Video

    opt = dict([('view', view),
            ('slice', slice_num),
            ('reference', ref_phase),
            ('phases', phases),
            ('breathing_time', breathing_time),
            ('amplitude', amplitude),
            ('video_time', video_time),
            ('frame_per_sec', frame_per_sec),
            ('random_amp', random_amp),
            ('overwrite', overwrite),
            ('debug', debug) ])

    video_4d(file_reference, files_transforms, folder_output, opt, list_trfm_masks, labels_names)

    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
