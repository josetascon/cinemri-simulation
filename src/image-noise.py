# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2020-10-10 11:26:42
# @Last Modified by:   jose
# @Last Modified time: 2021-08-04 10:01:23

import os
import argparse                 # argument parser
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

from noise import *

def main():
    # Arguments descriptions
    parser = argparse.ArgumentParser(description='Add noise an image')
    parser.add_argument("input_file", type=str,
                        help='Input file to add noise')
    parser.add_argument("output_file", type=str,
                        help='Output file with noise')
    parser.add_argument('-t','--type', type=str, default='gaussian',
                        help='Noise types: gaussian (default), saltpepper, speckle, rician.')
    parser.add_argument('-s','--stddev', type=float, default=10.0,
                        help='Noise standard deviation')
    parser.add_argument('-r', '--percentage', action='store_true',
                        help='Noise as percentage')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Plot noise')
    parser.add_argument('-w', '--overwrite', action='store_true',
                        help='Overwrite existent files')
    parser.add_argument('-d','--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v','--verbose', action='store_true',
                        help='Enable verbose mode')

    # Parse arguments
    args = parser.parse_args()
    
    file_input = args.input_file
    file_output = args.output_file
    str_type = args.type
    stddev = args.stddev
    overwrite = args.overwrite
    percentage = args.percentage
    plot = args.plot
    debug = args.debug
    verbose = args.verbose

    if verbose:
        print('Input file:\t', file_input)

    # Read the image
    try:
        image = sitk.ReadImage(file_input)
    except:
        print('Unable to read input image file.')

    output = sitk.Image()

    if verbose:
        print('Apply Noise:\t', str_type)

    if percentage:
        if str_type == 'gaussian':
            output = gaussian_noise_percentage(image, stddev)
        elif str_type == 'saltpepper':
            pass
        elif str_type == 'speckle':
            pass
        elif str_type == 'rician':
            pass
            output = rician_noise_percentage(image, stddev)
        else:
            print('Unsupported noise type')
    else:
        if str_type == 'gaussian':
            output = sitk.AdditiveGaussianNoise(image, stddev)
        elif str_type == 'saltpepper':
            output = sitk.SaltAndPepperNoise(image, stddev)
        elif str_type == 'speckle':
            output = sitk.SpeckleNoise(image, stddev)
        elif str_type == 'rician':
            pass
            # output = RicianNoise(image, stddev)
        else:
            print('Unsupported noise type')

    if plot:
        if verbose:
            print('Plotting ...')
        img = sitk.GetArrayFromImage(image)
        out = sitk.GetArrayFromImage(output)

        plt.figure()
        plt.subplot(121)
        plt.imshow(img, cmap=plt.cm.gray)
        plt.axis('off')
        plt.title('Input Image')
        plt.subplot(122)
        plt.imshow(out, cmap=plt.cm.gray)
        plt.axis('off')
        plt.title('Noise Image')
        plt.show()

    if verbose:
        print('Output file:\t', file_output)
    
    if not debug:
        sitk.WriteImage(output, file_output)
    return


if __name__ == "__main__":
    # execute only if run as a script
    main()
