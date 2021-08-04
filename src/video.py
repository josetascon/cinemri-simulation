# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2020-10-10 11:26:42
# @Last Modified by:   jose
# @Last Modified time: 2021-08-03 17:47:50

import os
import sys
import numpy as np
import SimpleITK as sitk

from folder import *
from image import *

def is_increase(list_path):
    increase = True
    if len(list_path) == 1: return increase
    if np.sign(list_path[1] - list_path[0])==-1 or ((list_path[1] - 1) != list_path[0]): # Check if decrease
        increase = False
    return increase

def select_path( phases, ref_num, floor_phase, ceil_phase ):
    list_num_images = list(range(phases))
    floor_path = shortest_path_of_image_sequence( list_num_images, ref_num, floor_phase )
    ceil_path = shortest_path_of_image_sequence( list_num_images, ref_num, ceil_phase )
#         print(floor_path)
#         print(ceil_path)

    list_path = []
    if (is_increase(floor_path)):
        if (not is_increase(ceil_path)): ceil_path = ceil_path + [floor_phase]
        list_path = ceil_path
    else:
        list_path = floor_path
    
    return list_path
    
def path_to_compose_transform_files( list_path, trfm_files, verbose = True ):
    if (not len(list_path) > 1): return []
    increase = is_increase(list_path)
    if verbose:
        print('Path: ', list_path)
        print('Increase:', increase)
    
    compose_trfm_files = []

    for k in range(len(list_path)-1,0,-1):
        if increase:
            prefix_str = '{}to{}_'.format(str(list_path[k-1]).zfill(2),str(list_path[k]).zfill(2))
            end_str = 'InverseWarp'
        else:
            prefix_str = '{}to{}_'.format(str(list_path[k]).zfill(2),str(list_path[k-1]).zfill(2))
            end_str = 'Warp'

        dfield_trfms_file = filter_folders_prefix([prefix_str + '0' + end_str], trfm_files)[0]
        compose_trfm_files.append(dfield_trfms_file)
    return compose_trfm_files

def multiply_multichannel(vimage, constant):
    '''
    Input
        vimage = sitk vector image (multichannel)
        constant =  float
    Output:
        vout
    '''
    channels = []
    for i in range(vimage.GetNumberOfComponentsPerPixel()):
        channels.append(sitk.VectorIndexSelectionCast(vimage,i)*constant)
    vout = sitk.Compose(channels)
    return vout

def image3d_multichannel_to_slice( image, slice_value, view = 'axial' ):
    '''
    Function to get an 2D slice from a 3D image. The orientation in coronal and sagittal is changed
    due to Dicom format
    Input:
        image: sitk.Image 3D
        slice_value: int. Slice number
        view: string. Point of view [axial, sagittal or coronal]
    Output:
        slice_image: list of of sitk.Image 2D
    '''
    
    if view == 'axial':     # axial = xy
        x = sitk.VectorIndexSelectionCast(image,0)
        y = sitk.VectorIndexSelectionCast(image,1)
        slice_image = sitk.Compose(image3d_to_slice(x,slice_value,view), image3d_to_slice(y,slice_value,view))
    elif view == 'coronal': # coronal = xz. Invert z coordinate
        x = sitk.VectorIndexSelectionCast(image,0)
        z = sitk.VectorIndexSelectionCast(image,2)
        slice_image = sitk.Compose(image3d_to_slice(x,slice_value,view), image3d_to_slice(z,slice_value,view))
    elif view == 'sagittal': # sagital = yz. Invert z coordinate
        y = sitk.VectorIndexSelectionCast(image,1)
        z = sitk.VectorIndexSelectionCast(image,2)
        slice_image = sitk.Compose(image3d_to_slice(y,slice_value,view), image3d_to_slice(z,slice_value,view))
    else:
        slice_image = 0
    return slice_image

def read_dfield_compose( compose_trfm_files, amplitude = 1.0, proportion = 1.0, slice_num = None, view = '' ):
    compose_trfm = sitk.CompositeTransform(3)
    for i,dfile in enumerate(compose_trfm_files):
        print(dfile)
        dfield_image = sitk.ReadImage(dfile)                    # Read deformation field as image (inverse file provided)
        if (amplitude != 1.0): dfield_image = multiply_multichannel(dfield_image,amplitude)
        if (i == 0): dfield_image = multiply_multichannel(dfield_image,proportion)
        dfield_trfm = sitk.DisplacementFieldTransform(dfield_image)  # Read deformable transform
#         print(image_info(dfield_slice))
#         print(transform_info(dfield_trfm))
        if (i == 0 ): compose_trfm = sitk.Transform(dfield_trfm)
        else: compose_trfm.AddTransform(dfield_trfm)
    return compose_trfm


def image3d_slice( image, slice_value, view = 'axial' ):
    '''
    Function to get an 2D slice from a 3D image. The orientation in coronal and sagittal is changed
    due to Dicom format
    Input:
        image: sitk.Image 3D
        slice_value: int. Slice number
        view: string. Point of view [axial, sagittal or coronal]
    Output:
        slice_image: list of of sitk.Image 2D
    '''
    if view == 'axial':
        slice_image = image[:,:,slice_value]    # axial = xy
    elif view == 'coronal':
        slice_image = image[:,slice_value,:]    # coronal = xz. Invert z coordinate
    elif view == 'sagittal':
        slice_image = image[slice_value,:,:]    # sagital = yz. Invert z coordinate
    else:
        slice_image = 0
    return slice_image

def extract_image_masks(image, file_rt, label_strings, verbose = True):
    if verbose: print('Labels in dicom file: \n', read_contours_labels(file_rt))
    label_object = []
    color_object = []
    mask_object = []
    for label_str in label_strings:
        contour, color = read_contours(file_rt,label_str)
        mask = contour_to_mask_3d( contour, image )
        if verbose: print(image_info(mask, 'Segment ' + label_str))
        label_object.append(label_object)
        color_object.append(color)
        mask_object.append(mask)
    return mask_object, color_object

def video_4d( reference_file, transform_files, output_folder, 
            opt = 0, extra_images = [], extra_folders = [] ):

    # in case opt is empty or missing parameters
    if opt == 0:
        opt = dict()
    if not 'view' in opt:           opt['view']           = 'sagittal'
    if not 'slice' in opt:          opt['slice']          = 100
    if not 'reference' in opt:      opt['reference']      = 0
    if not 'phases' in opt:         opt['phases']         = 10
    if not 'breathing_time' in opt: opt['breathing_time'] = 4.0
    if not 'amplitude' in opt:      opt['amplitude']      = 1.0
    if not 'video_time' in opt:     opt['video_time']     = 20.0
    if not 'frame_per_sec' in opt:  opt['frame_per_sec']  = 4
    if not 'random_amp' in opt:     opt['random_amp']     = False
    if not 'overwrite' in opt:      opt['overwrite']      = False
    if not 'debug' in opt:          opt['debug']          = False
    if not 'verbose' in opt:        opt['verbose']        = False

    # print('W:', opt['overwrite'])
    
    # read the reference image
    img3d = sitk.ReadImage(reference_file)
    img = image3d_slice(img3d, opt['slice'], opt['view'])
    if opt['verbose']: print(image_info(img), 'CineMR Image Information')
    minmax = sitk.MinimumMaximumImageFilter()
    minmax.Execute(img)
    # print('min {}, max {}\n'.format(minmax.GetMinimum(), minmax.GetMaximum()))
    
    # extra images
    img2d_extra = []
    for img_ext in extra_images:
        img2d_extra.append(image3d_slice(img_ext, opt['slice'], opt['view']))
    
    # time variables
    ts = 1/opt['frame_per_sec']
    time = np.arange(0.0,opt['video_time'],ts)
    phase_per_sec = opt['breathing_time']/opt['phases']
#     print(time)

    # amplitude
    amplitude = opt['amplitude']
    if opt['random_amp']: amplitude = 1.0 # If random, first cycle is regular
    
    # make output folders
    folder_out = os.path.join(output_folder, 'image/')
    # if not opt['debug']: 
    os.system('mkdir -p ' + folder_out)            # make directory
    folder_out_extras = []
    if (extra_folders == []):
        for k,_ in enumerate(img2d_extra):
            folder_ext = os.path.join(output_folder, 'struct{:02d}/'.format(k))
            if not opt['debug']: os.system('mkdir -p ' + folder_ext)    # make directory
            folder_out_extras.append(folder_ext)
    else:
        for folder in extra_folders:
            folder_ext = os.path.join(output_folder, folder)
            if not opt['debug']: os.system('mkdir -p ' + folder_ext)    # make directory
            folder_out_extras.append(folder_ext)

    # assert extra
    assert len(extra_images) == len(folder_out_extras)


    # Prepare for loop
    info = '{:^5}  {:^5}  {:^5}  {:^5}  {:^5}  {:^5}'\
              .format('ts', 'cycle', 'phase', 'res', '%', 'amp')
    it = 0
    new_cycle = 0.0

    # Check if existing files in output
    existing_files = listdir_fullpath(folder_out)
    num_files = len(existing_files)
    if num_files > 0:
        print('Existing files, use option -w to overwrite')
        if not opt['overwrite']:
            it = num_files
            time = time[num_files:]
    
    # if opt['overwrite']:
            

    for t in time:
        # initialize image to write
        img_warped = img
        
        # time variables per iteration
        cycle = t%opt['breathing_time']
        if (abs(cycle - opt['breathing_time']) < 1e-6): cycle = 0.0 # this to avoid numerical aprox error of python. e.g when bt=3.6, t = 18 then cycle = 3.5999999
        
        # detect reboot cycle
        if (new_cycle > cycle) and opt['random_amp']:
            # print('random')
            amplitude = np.random.uniform(1.0,2.0)

        new_cycle = cycle
        floor_phase = int(np.floor(cycle/phase_per_sec))
        ceil_phase = int(np.ceil(cycle/phase_per_sec))%10
        residual = cycle%phase_per_sec
        proportion = residual/phase_per_sec
        
        # print iteration info
        print()
        print(info)
        print('{:5.2f}  {:5.2f}  {:2d}-{:<2d}  {:5.2f}  {:5.2f}  {:5.2f}'\
              .format(t, cycle, floor_phase, ceil_phase, residual, proportion, amplitude))
        
        # find the path
        list_path = select_path(opt['phases'], opt['reference'], floor_phase, ceil_phase)
        #         print(list_path)
        proportion = 1-proportion if (not is_increase(list_path)) else proportion
#         print('% = ', proportion)
        
        #compose transform
        compose_trfm_files = path_to_compose_transform_files(list_path, transform_files, opt['verbose'])
        if opt['verbose']: print(fullpath_to_localpath(compose_trfm_files))
        
        if (not compose_trfm_files == [] and not opt['debug']):
            # read the transforms
            trfm = read_dfield_compose( compose_trfm_files, amplitude, proportion, opt['slice'], opt['view'] )
            # transform the image
            img3d_warped = sitk.Resample(img3d, trfm, sitk.sitkLinear, 0.0)
            # slice
            img_warped = image3d_slice(img3d_warped, opt['slice'], opt['view'])
            
            # extra images
            for i,img_ext in enumerate(extra_images):
                # transform the image
                img3d_extra_warped = sitk.Resample(img_ext, trfm, sitk.sitkLinear, 0.0)
                # slice
                img2d_extra[i] = image3d_slice(img3d_extra_warped, opt['slice'], opt['view'])
            
        
        # change direction
        img_warped.SetDirection([-1,0,0,-1])
        # print(image_info(img_warped))
        
        for img_ext in img2d_extra:
            img_ext.SetDirection([-1,0,0,-1])
        
        # write the image
#         img_warped = sitk.Cast(img_warped, sitk.sitkUInt16)
        file_out = os.path.join(folder_out, 'image_{:04d}.nii'.format(it))
        print(file_out)
        if not opt['debug']: sitk.WriteImage(img_warped, file_out)
        
        file_extra = ''
        for k,img_ext in enumerate(img2d_extra):
            if (extra_folders == []):
                file_extra = os.path.join(folder_out_extras[k], 'structure_{:04d}.nii'.format(it))
            else:
                file_extra = os.path.join(folder_out_extras[k], extra_folders[k] + '_{:04d}.nii'.format(it))
            print(file_extra)
            if not opt['debug']: sitk.WriteImage(img_ext, file_extra)
        
        it = it + 1
    