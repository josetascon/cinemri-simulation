# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2021-08-03 15:39:02
# @Last Modified by:   jose
# @Last Modified time: 2021-08-03 17:13:57

import pydicom as dcm
import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk

from skimage.draw import polygon
from skimage.color import rgb2gray, gray2rgb

def image_info( image, text = 'Image Information' ):
    '''
    Return a string with image information details. Pixel type, dimensions, scale.
    Input: 
        image: sitk.Image
        text: string. Title to the output
    Output: string
    '''
    info = '\n===== '+ text +' ====='
    info += '\nPixel type: \t\t' + str(image.GetPixelIDTypeAsString())
    info += '\nPixel channels: \t' + str(image.GetNumberOfComponentsPerPixel())
    info += '\nDimensions: \t\t' + str(image.GetDimension())
    info += '\nSize: \t\t\t' + str(image.GetSize())
    info += '\nLength (mm): \t\t' + str(image.GetSpacing())
    info += '\nOrigin (mm): \t\t' + str(image.GetOrigin())
    info += '\nDirection: \t\t' +  str(image.GetDirection())
    info += '\nTotal Elements: \t' + str(image.GetNumberOfPixels())
    info += '\n'
    return info

def transform_image(image, ref_image, transform, interpolator = sitk.sitkLinear, default_value = 0.0):
    # Apply a transform to an image. The output image will have the same coordinates as the reference
    # Inputs: sitk.Image, sitk.Image, sitk.Transform, sitk.InterpolatorEnum, double
    # Output: sitk.Image
    return sitk.Resample(image, ref_image, transform, interpolator, default_value)

def read_dfield_transform(dfield_file, compose_trfm=None, verbose=False):
    
    if verbose: 
        print('Transform: ' + str(fullpath_to_localpath([dfield_file])))

    dfield_image = sitk.ReadImage(dfield_file)              # Read deformation field as image (inverse file provided)
    dfield = sitk.DisplacementFieldTransform(dfield_image)  # Read deformable transform
    if compose_trfm == None:
        return dfield
    else:
        compose_trfm.AddTransform(dfield)
        return compose_trfm

def read_compose_transform(dfield_file, affine_file, compose_trfm = None, inverse=False, verbose=False):
    # Compose tranform to convert images (do not use for points)
    # Warp coordinates in fixed space (x0)
    # Default refers to moving -> fixed:  I0' = Warp * Taff * I1
    # Inverse refers to fixed -> moving:  I1' = Taff-1 * Warp-1 * I0
    # Input:
    # dfield_file: string with dfield file name
    # affine_file: string with affine file name
    # Output:
    # compose_trfm: sitk.Transform

    if compose_trfm == None:
        compose_trfm = sitk.CompositeTransform(3)

    if verbose:
        print('Transform: ' + str(fullpath_to_localpath([dfield_file])))
        print('Transform: ' + ('[Inv]' if inverse else '')  + str(fullpath_to_localpath([affine_file])))

    # Read transforms
    affine = sitk.ReadTransform(affine_file)                # Read affine transform
    dfield = read_dfield_transform(dfield_file)             # Read deformation field transform (inverse file provided)

    if inverse:
        # compose_trfm.AddTransform(affine)                       # Add affine to composition. First transform to apply
        compose_trfm.AddTransform(affine.GetInverse())          # Inverse the affine transform. Last transform to apply
        compose_trfm.AddTransform(dfield)                       # Add inverse deformation field. First transform to apply
    else:
        # Default
        compose_trfm.AddTransform(dfield)                       # Add dfield to composition. Last transform to apply
        compose_trfm.AddTransform(affine)                       # Add affine to composition. First transform to apply
    return compose_trfm

def read_contours_labels( dcm_file ):
    '''
    Read the labels inside rt dicom file
    Input:
        dcm_file: string. File name of the dicom rt
    Output:
        list of strings
    '''
    ds = dcm.read_file(dcm_file)            # Create filedataset
    obsr = ds.RTROIObservationsSequence     # Description of contours
    labels = []
    for k in range(len(obsr)):
        labels.append(obsr[k].ROIObservationLabel)    # check the desired label
    return labels

def read_contours( dcm_file, label ):
    '''
    Read contours of specific label in dicom file
    Input:
      dcm_file: string. File name of the dicom rt
      label: string. Name of the contour that is desired to extract from the dicom file
    Output:
        contours : list of list. The globlal len refer to the amount of slices with contours. 
                The interal len is variable depending of the number of point defining the contour.
                The internal list contains 3D coordinates as: [x1, y1, z1, x2, y2, z2, ...]
        color: list with RGB color. Values from 0 to 255
    '''
    ds = dcm.read_file(dcm_file)            # Create filedataset
    obsr = ds.RTROIObservationsSequence     # Description of contours
    ctrs = ds.ROIContourSequence            # Contours values

    # labels = []
    contours = []
    color = []
    for k in range(len(obsr)):
        if label == obsr[k].ROIObservationLabel:    # check the desired label
            color = list(ctrs[k].ROIDisplayColor)   # read the color
            ctr_seq = ctrs[k].ContourSequence       
            for j in range(len(ctr_seq)):           # Explore the contour
                contours.append(list(ctr_seq[j].ContourData))
            break
    return contours, color

def point_world_to_image( point_xyz, origin, spacing, direction):
    # Function to convert a world coordinate point (metric) to an image point (pixel coordinates)
    # Inputs: As tuples obtained from sitk. Also support numpy array [1,3]
    # Output: Numpy array size [3,1]

    # Cast the inputs to numpy arrays
    xyz_np = np.asarray(point_xyz)
    d_np = np.asarray(direction).reshape([3,3]) # 3D matrix direction
    s_np = np.diag(np.asarray(spacing))
    o_np = np.asarray(origin)

    # Apply the transformation
    # ds = np.linalg.inv(d_np@s_np) # Find the inverse matrix
    ds = np.linalg.inv(s_np)@np.linalg.inv(d_np)
    uvw = (ds)@(xyz_np - o_np).transpose()
    return uvw.transpose()

def contour_world_to_image( contour, ref_image ):
    # Transform the contour
    # Input:
    #   contour: List
    #   ref_image: sitk.Image
    # Output:
    #   cc: numpy array
    ctr_np = np.asarray(contour)
    num_pts = int(ctr_np.size/3)
    ctr = ctr_np.reshape([num_pts, 3])
    cc = point_world_to_image( ctr, ref_image.GetOrigin(), 
                ref_image.GetSpacing(), ref_image.GetDirection() )
    return cc

def get_zvalue_from_contour( contour, ref_image  ):
    # Function to obtain the z pixel value form contours of dicom rt files. 
    # Use only the first point of contour because the contouring is made in the axial slices
    # Input
    #   contours: list of list. The contour has a z value fix for all the points. 
    #           Therefore only the first point is used
    #   ref_image: sitk.Image
    # Output:
    #   zvalue: int
    point = contour[0:3] # First point
    uvw = point_world_to_image( point, ref_image.GetOrigin(), 
                ref_image.GetSpacing(), ref_image.GetDirection() )
    zvalue = int(uvw[2]) # z pixel coordinate
    return zvalue

def contour_to_mask_2d( contour, ref_image, return_numpy = False ):
    # Function to create a 2d image mask using contour values
    # Input:
    #   contour: list with 3xn points. Ignored z coordinate of the points
    #   ref_image: sitk.Image in 2d
    #   return_numpy: bool. Return a numpy array or a sitk.Image
    # Output:
    #   image: sitk.Image or numpy_array
    ctr_np = np.asarray(contour)
    num_pts = int(ctr_np.size/3)
    ctr = ctr_np.reshape([num_pts, 3])

    size = ref_image.GetSize()
    img = np.zeros((size[1],size[0]), dtype=np.uint8)
    c = ctr[:,0]                # Colunm values
    r = ctr[:,1]                # Row values
    rr, cc = polygon(r, c)      
    # print(rr)
    # image[rr, cc] = 1
    img[rr, cc] = 1
    if return_numpy:
        return img
    else:
        image = sitk.GetImageFromArray(img)
        image.CopyInformation(slice)
        return sitk.Cast(image,slice.GetPixelID())

def contour_to_mask_3d( contours, ref_image, return_numpy = False ):
    # Function to create a 3D mask using contours
    # Input
    #   contours: list of list
    #   ref_image: sitk.Image. Reference 3D image
    # Output
    #   mask_image: sitk.Image or numpy array. Image with the same size and coordinates as ref_image
    size = ref_image.GetSize()
    mask_image = np.zeros((size[2],size[1],size[0]), dtype=np.uint8) # Create empty image with same properties
    for c in range(len(contours)):
        z = get_zvalue_from_contour( contours[c], ref_image )
        cc = contour_world_to_image(contours[c], ref_image)
        mask2d = contour_to_mask_2d(cc, ref_image[:,:,z], return_numpy = True)
        mask_image[z,:,:] = mask_image[z,:,:] + mask2d # in case of multiple contours in the same slice
        # print(z)
        # print(image_info(mask2d))
    if return_numpy:
        return mask_image
    else:
        mask = sitk.GetImageFromArray(mask_image)
        mask.CopyInformation(ref_image)
        return sitk.Cast(mask,ref_image.GetPixelID())

def image3d_to_slice( image, slice_value, view = 'axial', direct=False ):
    '''
    Function to get an 2D slice from a 3D image. The orientation in coronal and sagittal is changed
    due to Dicom format
    Input:
        image: sitk.Image 3D
        slice_value: int. Slice number
        view: string. Point of view [axial, sagittal or coronal]
        direct: bool variable. Regular behavior to invert z axis for compatibility with matplotlib
    Output:
        slice_image: list of of sitk.Image 2D
    '''
    if view == 'axial':
        slice_image = image[:,:,slice_value]        # axial = xy
    elif view == 'coronal':
        if direct: slice_image = image[:,slice_value,:]     # coronal = xz.
        else:      slice_image = image[:,slice_value,::-1]  # coronal = xz. Invert z coordinate
    elif view == 'sagittal':
        if direct: slice_image = image[slice_value,:,:]     # sagital = yz.
        else:      slice_image = image[slice_value,:,::-1]  # sagital = yz. Invert z coordinate
    else:
        slice_image = 0
    return slice_image

def label_overlay( image_2d, label, color ):
    '''
    Function to put a color label over an image 2D. 
    Input:
        image_2d: sitk.Image 2D (gray)
        label: sitk.Image 2D
        color: tuple, list or numpy array (3 elements, values from 0-255 or 0-1)
    Output:
        image: sitk.Image 2D (RGB - sitkVector)
    '''
    image2 = sitk.RescaleIntensity(image_2d, outputMinimum = 0.0, outputMaximum = 1.0) 
    # Always ensure scale values 0 to 1. This is necessary for label overlay.
    image_np = sitk.GetArrayFromImage(image2)
    if image_np.ndim == 2:
        image_rgb = gray2rgb(image_np)
    else:
        image_rgb = image_np
    border_np = sitk.GetArrayFromImage(label)
    color_np = np.asarray(color)
    color_np = color_np/np.max(color_np)

    # Assign the color using the label image. For values where the label is 1.0
    size = image_rgb.shape
    for i in range(size[0]):
        for j in range(size[1]):
            if border_np[i,j] > 0.5:
                image_rgb[i,j,:] = np.asarray(color_np)
    image = sitk.GetImageFromArray(image_rgb, True) 
    image.CopyInformation(image_2d)  # Copy image metadata
    return image

def imshow_2d( image_itk, title = '', show = True, axis = False, cmap = plt.cm.gray, colorbar = False ):
    # Function to show a 2D image with matplotlib
    # Inputs: sitk.Image, string with title
    # Output: None
    channels = image_itk.GetNumberOfComponentsPerPixel() # get the number of channels
    image_npa = sitk.GetArrayViewFromImage(image_itk) # get a copy as numpy array with the image data
    # image_npa = equalize_hist(image_npa)
    spacing = image_itk.GetSpacing() # scale in mm
    size = image_itk.GetSize()       # pixel width and height
    extent = (0, np.ceil(spacing[0]*size[0]), np.ceil(spacing[1]*size[1]), 0) #image limits
    if channels == 1: # set the color map according to the channels
        plt_im = plt.imshow(image_npa, cmap = cmap, extent = extent) # 1 channel for monochrome image
    else:
        plt_im = plt.imshow(image_npa, extent = extent)     # default color map of pyplot
    plt.title(title)
    if not axis: plt.axis('off') # disable to see axis
    if show: plt.show()          # stop show, useful when subplotting
    if colorbar: plt.colorbar()
    return plt_im

def shortest_path_of_image_sequence( list_range, ref_num, value ):
    # Find the shortest path in a sequence of images registered sequentially. 
    # The input is a list of the sequence of images. The output is a list with the sequence
    # of images to go through
    # Input:
    #   list_range: list of integers (integer represent an image number)
    #   ref_num: int. Reference image (index)
    #   value: int. Value number where the path is found from the reference
    # Output:
    #   list: list of integers with the shortest path
    id0 = list_range.index(ref_num)  # Reference index
    idv = list_range.index(value)    # Value index
    mx = list_range[-1]              # sorted list, therefore maximum is last element
    # print('Reference:',id0, ', Value: ',idv)
    dist1 = abs(id0 - idv)           # Compute the direct distance (incremental)
    dist2 = len(list_range) - dist1  # Compute the distance in the other way (inverse)
    # print('Distances: ', dist1,'-' , dist2)

    # Return the path from reference to value index. This is a sublist with succesive order of images
    if dist1 <= dist2:
        if id0 > idv:
            if idv == 0:
                return list_range[id0::-1]
            return list_range[id0:idv-1:-1]
        else:
            return list_range[id0:idv+1]
    else:
        if id0 > idv:
            return list_range[id0:] + list_range[0:idv+1]
        else: 
            return list_range[id0::-1] + list_range[-1:idv-1:-1]