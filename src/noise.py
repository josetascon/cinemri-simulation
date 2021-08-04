# -*- coding: utf-8 -*-
# @Author: jose
# @Date:   2020-10-10 11:26:42
# @Last Modified by:   jose
# @Last Modified time: 2021-06-08 22:43:15

import os
import numpy as np
import SimpleITK as sitk

# from imutils.image import image_info

def gaussian_noise_percentage(image, percent):
    # how to: https://stackoverflow.com/questions/31834803/how-to-add-5-percent-gaussian-noise-to-image

    # stats
    stats = sitk.StatisticsImageFilter()
    stats.Execute(image)
    minx = stats.GetMinimum()
    maxx = stats.GetMaximum()
    meanx = stats.GetMean()
    stdx = stats.GetSigma()
    # print('Image stats \nmin {}, max {}, mean {}, std {}'.format(minx,maxx,meanx,stdx))

    # normalize image
    img = sitk.ShiftScale( sitk.Cast( image, sitk.sitkFloat64 ), -minx, 1/(maxx - minx) )
    # img = sitk.RescaleIntensity( sitk.Cast( image, sitk.sitkFloat64 ), 0.0, 1.0 ) # equivalent
    
    # stats to get std
    stats = sitk.StatisticsImageFilter()
    stats.Execute(img)
    sigma = stats.GetSigma()
    # print(sigma)
    
    # new_sigma = sigma * percent
    new_sigma = sigma * percent * (maxx - minx) + minx
    # print(new_sigma)

    # gaussian noise
    output = sitk.AdditiveGaussianNoise(image, new_sigma)

    # stats = sitk.StatisticsImageFilter()
    # stats.Execute(output)
    # minx = stats.GetMinimum()
    # maxx = stats.GetMaximum()
    # meanx = stats.GetMean()
    # stdx = stats.GetSigma()
    # print('Image stats \nmin {}, max {}, mean {}, std {}'.format(minx,maxx,meanx,stdx))
    return output

def ricernd(v, s):
    # See https://www.mathworks.com/matlabcentral/fileexchange/14237-rice-rician-distribution
    x = s * np.random.normal(size=np.size(v)).reshape(v.shape) + v
    y = s * np.random.normal(size=np.size(v)).reshape(v.shape)
    r = np.sqrt(x**2.0 + y**2.0)
    return r

def rician_noise_percentage(image, percent):
    # stats
    stats = sitk.StatisticsImageFilter()
    stats.Execute(image)
    minx = stats.GetMinimum()
    maxx = stats.GetMaximum()
    meanx = stats.GetMean()
    stdx = stats.GetSigma()
    # print('Image stats \nmin {}, max {}, mean {}, std {}'.format(minx,maxx,meanx,stdx))

    # normalize image
    imgf64 = sitk.Cast( image, sitk.sitkFloat64 )
    img = sitk.ShiftScale( imgf64, -minx, 1/(maxx - minx) )
    
    # stats to get std
    stats = sitk.StatisticsImageFilter()
    stats.Execute(img)
    sigma = stats.GetSigma()
    # print('Sigma:', sigma)
    
    # new_sigma = sigma * percent
    new_sigma = sigma * percent * (maxx - minx) + minx
    # print('Sigma new:', new_sigma)

    # rician noise
    np_image = sitk.GetArrayFromImage(image)
    np_noise = ricernd(np_image, new_sigma)
    noise = sitk.GetImageFromArray(np_noise)
    # noise = sitk.Cast( noise, image.GetPixelID() )
    noise.CopyInformation(image)

    stats.Execute(noise)
    mino = stats.GetMinimum()
    maxo = stats.GetMaximum()
    meano = stats.GetMean()
    stdo = stats.GetSigma()
    # print('Noise stats \nmin {}, max {}, mean {}, std {}'.format(mino,maxo,meano,stdo))

    # print(image_info(image))
    # print(image_info(noise))

    output = noise
    # output = imgf64 + noise - meano

    # stats.Execute(output)
    # mino = stats.GetMinimum()
    # maxo = stats.GetMaximum()
    # meano = stats.GetMean()
    # stdo = stats.GetSigma()
    # print('Image stats \nmin {}, max {}, mean {}, std {}'.format(mino,maxo,meano,stdo))

    # normalize image
    # output = sitk.ShiftScale( output, -mino, 1/(maxo - mino) )
    # output = output*(maxx-minx)+minx
    # output = sitk.Cast( output, image.GetPixelID() )

    output = sitk.Clamp( output, image.GetPixelID(), minx, maxx )
    return output

def rician_noise_old(image, s):
    v = sitk.GetArrayFromImage(image)
    np_noise = ricernd(v, s)
    noise = sitk.GetImageFromArray(np_noise)
    noise.CopyInformation(image)

    minmax = sitk.MinimumMaximumImageFilter()
    minmax.Execute(image)
    img_min = minmax.GetMinimum()
    img_max = minmax.GetMaximum()
#     print('Image: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))
#     minmax.Execute(noise)
#     print('Noise: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))

    low = sitk.Cast((image>(0.05*img_max)), sitk.sitkFloat64)
    image_noise = (image + noise)*low
    image_noise = image_noise*sitk.Cast((image_noise>img_min), sitk.sitkFloat64)
    image_noise = image_noise*sitk.Cast((image_noise<img_max), sitk.sitkFloat64)
    
#     minmax.Execute(image_noise)
#     img_min = minmax.GetMinimum()
#     img_max = minmax.GetMaximum()
    # image_noise = sitk.AdditiveGaussianNoise(image, 20.0, 0.0)
#     print('Image+Noise: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))
    return image_noise


def gaussian_noise_old(image, std, mean = 0.0):
    np_noise = np.random.normal(mean, std, image.GetSize());
    np_noise = np_noise.transpose()
    noise = sitk.GetImageFromArray(np_noise)
    noise.CopyInformation(image)

    minmax = sitk.MinimumMaximumImageFilter()
    minmax.Execute(image)
    img_min = minmax.GetMinimum()
    img_max = minmax.GetMaximum()
#     print('Image: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))
#     minmax.Execute(noise)
#     print('Noise: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))

    low = sitk.Cast((image>(0.05*img_max)), sitk.sitkFloat64) # Use to avoid noise in background
    image_noise = (image + noise)*low
    image_noise = image_noise*sitk.Cast((image_noise>img_min), sitk.sitkFloat64)
    image_noise = image_noise*sitk.Cast((image_noise<img_max), sitk.sitkFloat64)
    
#     minmax.Execute(image_noise)
#     img_min = minmax.GetMinimum()
#     img_max = minmax.GetMaximum()
    # image_noise = sitk.AdditiveGaussianNoise(image, 20.0, 0.0)
#     print('Image+Noise: min {}, max {}'.format(minmax.GetMinimum(), minmax.GetMaximum()))
    return image_noise