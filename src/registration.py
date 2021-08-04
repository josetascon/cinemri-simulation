# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2021-08-02 20:40:53
# @Last Modified by:   jose
# @Last Modified time: 2021-08-02 22:33:35

import os                       # os library

def register_sequential_syn(file_4dct00, file_mr, output_path, debug = True, overwrite = True):
    # Output file names
    out_prefix = '{}to{}_'.format(os.path.splitext(os.path.basename(file_4dct00))[0][-2:], 
                                os.path.splitext(os.path.basename(file_mr))[0][-2:])
    output = os.path.join(output_path, out_prefix)
    # print(out_prefix)

    # Check if files already exist
    output_already0 = out_prefix + '0Warp.nii.gz'
    output_already1 = out_prefix + '0InverseWarp.nii.gz'

    write = True
    files_overwrite = []
    if overwrite:
        write = True
    else:
        try:
            files_overwrite = os.listdir(output_path)
        except:
            pass
        if output_already0 in files_overwrite:
            write = False
            os.system('echo [Warning] Existing registration {}. Continue. Use option -w to overwrite'.format(output_already0))
        elif output_already1 in files_overwrite:
            write = False
            os.system('echo [Warning] Existing registration {}. Continue. Use option -w to overwrite'.format(output_already1))
        else:
            write = True
    
    # Command for registration
    cmd = 'antsRegistration --verbose 1 --dimensionality 3 --float 0\
    --output [{}, {}Warped.nii.gz]\
    --interpolation Linear --use-histogram-matching 0\
    --winsorize-image-intensities [0.005,0.995]\
    --transform SyN[0.1,3,0]\
    --metric CC[{},{},1,4] --convergence [250x250x90x30,1e-6,15]\
    --shrink-factors 8x4x2x1 --smoothing-sigmas 3x2x1x0vox\
    '.format(output, output, file_4dct00, file_mr)

    # Execute the command
    if write:
        os.system('echo ' + cmd)
        if not debug:
            os.system(cmd)

def register_4dct00_mr(file_4dct00, file_mr, output_path, debug = True, overwrite = True):

    # Output file names
    out_prefix = '4dct00_to_mr_'
    output = os.path.join(output_path, out_prefix)

    # Check if file already exist
    output_already = out_prefix + '1Warp.nii.gz'
    
    write = True
    files_overwrite = []
    if overwrite:
        write = True
    else:
        try:
            files_overwrite = os.listdir(output_path)
        except:
            pass
        if output_already in files_overwrite:
            write = False
            os.system('echo [Warning] Existing registration {}. Continue. Use option -w to overwrite'.format(output_already))
        else:
            write = True

    # Command for registration
    cmd = 'antsRegistration --verbose 1 --dimensionality 3 --float 0\
    --output [{},{}Warped.nii.gz,{}InverseWarped.nii.gz]\
    --interpolation Linear --use-histogram-matching 0\
    --winsorize-image-intensities [0.005,0.995]\
    --initial-moving-transform [{},{},1]\
    --transform Rigid[0.1] --metric MI[{},{},1,32,Regular,0.25]\
    --convergence [1000x500x250x100,1e-6,10] --shrink-factors 12x8x4x2 --smoothing-sigmas 4x3x2x1vox\
    --transform Affine[0.1] --metric MI[{},{},1,32,Regular,0.25]\
    --convergence [1000x500x250x100,1e-6,10] --shrink-factors 12x8x4x2 --smoothing-sigmas 4x3x2x1vox\
    --transform SyN[0.1,3,0] --metric CC[{},{},1,4]\
    --convergence [250x200x180x90x25,1e-6,10] --shrink-factors 10x6x4x2x1 --smoothing-sigmas 5x3x2x1x0vox\
    '.format(output, output, output, file_4dct00, file_mr, file_4dct00, file_mr, 
    file_4dct00, file_mr, file_4dct00, file_mr)

    # Execute the command
    if write:
        os.system('echo ' + cmd)
        if not debug:
            os.system(cmd)