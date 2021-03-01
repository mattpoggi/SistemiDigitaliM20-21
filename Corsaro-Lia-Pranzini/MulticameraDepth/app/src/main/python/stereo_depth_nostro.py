import numpy as np
import cv2
import argparse
import sys
import time
from calibration_store import load_stereo_coefficients

def depth_map(imgL, imgR):
    """ Depth map calculation. Works with SGBM and WLS. Need rectified images, returns depth map ( left to right disparity ) """
    # SGBM Parameters -----------------
    window_size = 3  # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely

    left_matcher = cv2.StereoSGBM_create(
        minDisparity=-1,
        numDisparities=12*16,  # max_disp has to be dividable by 16 f. E. HH 192, 256
        blockSize=window_size,
        P1=8 * 3 * window_size,
        # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
        P2=32 * 3 * window_size,
        disp12MaxDiff=12,
        uniquenessRatio=10,
        speckleWindowSize=50,
        speckleRange=32,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )
    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
    # FILTER Parameters
    lmbda = 80000
    sigma = 1.3
    visual_multiplier = 6 #6

    wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)

    wls_filter.setSigmaColor(sigma)
    displ = left_matcher.compute(imgL, imgR)  # .astype(np.float32)/16
    dispr = right_matcher.compute(imgR, imgL)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    filteredImg = wls_filter.filter(displ, imgL, None, dispr)  # important to put "imgL" here!!!

    filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
    filteredImg = np.uint8(filteredImg)
    #filteredImg = cv2.applyColorMap(filteredImg, cv2.COLORMAP_AUTUMN)

    return filteredImg


def stereo_depth(calibration_file, left_source, right_source, is_real_time, save_path):

    K1, D1, K2, D2, R, T, E, F, R1, R2, P1, P2, Q = load_stereo_coefficients(calibration_file)  # Get cams params


    leftFrame =  cv2.imread(left_source,1)
    leftFrame = cv2.rotate(leftFrame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    leftFrame = cv2.resize(leftFrame, (1824,1368))
    #left_resized = cv2.resize(leftFrame, (0,0), fx=.3, fy=.3)
    #cv2.imshow('left(R)', original_resized)
        
    rightFrame = cv2.imread(right_source,1)
    rightFrame = cv2.rotate(rightFrame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    rightFrame = cv2.resize(rightFrame, (1824,1368))
    #right_resized = cv2.resize(rightFrame, (0,0), fx=.3, fy=.3)
    #cv2.imshow('right(R)', original_resized)
    height, width, channel = leftFrame.shape  # We will use the shape for remap

    # Undistortion and Rectification part!
    leftMapX, leftMapY = cv2.initUndistortRectifyMap(K1, D1, R1, P1, (width, height), cv2.CV_32FC1)
    left_rectified = cv2.remap(leftFrame, leftMapX, leftMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    left_rect_save = cv2.resize(left_rectified, (640,448))
    cv2.imwrite(save_path+"/left_rectified.jpg",left_rect_save)
    #original_resized = cv2.resize(left_rectified, (0,0), fx=.3, fy=.3)
    
    #cv2.imshow('retleft(R)', original_resized)
        
    rightMapX, rightMapY = cv2.initUndistortRectifyMap(K2, D2, R2, P2, (width, height), cv2.CV_32FC1)
    right_rectified = cv2.remap(rightFrame, rightMapX, rightMapY, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    right_rect_save = cv2.resize(right_rectified, (640,448))
    cv2.imwrite(save_path+"/right_rectified.jpg",right_rect_save)
    #original_resized = cv2.resize(right_rectified, (0,0), fx=.3, fy=.3)
    #cv2.imshow('retright(R)', original_resized)

    # We need grayscale for disparity map.
    gray_left = cv2.cvtColor(left_rectified, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right_rectified, cv2.COLOR_BGR2GRAY)

    disparity_image = depth_map(gray_left, gray_right)  # Get the disparity map
    cv2.imwrite(save_path+"/depth.jpg", disparity_image)
    return 1
    # Show the images
    #original_resized = cv2.resize(leftFrame, (0,0), fx=.3, fy=.3)
    #cv2.imshow('left(R)', original_resized)
    #original_resized = cv2.resize(rightFrame, (0,0), fx=.3, fy=.3)
    #cv2.imshow('right(R)', original_resized)
    #original_resized = cv2.resize(disparity_image, (0,0), fx=.2, fy=.2)
    #cv2.imshow('Disparity', original_resized)


    # Release the sources.
    #cv2.destroyAllWindows()
