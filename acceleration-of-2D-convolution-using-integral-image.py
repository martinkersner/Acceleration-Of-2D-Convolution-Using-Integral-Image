#!/usr/bin/python2

################################################################################
# Acceleration of 2D convolution using integral image
#
# @author       Martin Kersner
# @email        m.kersner@gmail.com
# @date         18/4/2013
# @last_update  21/4/2013
################################################################################

import cv2
from cv2 import cv 
import numpy as np

################################################################################
# Creates a miror borders (right and botttom) of given image.
# @param  img   image to make a mirror borders
# @param  n     size of border to mirrror
# @param  rows  number of rows
# @param  cols  number of cols
# @return       mirrored image
################################################################################
def mirrorImage(img, n, rows, cols):
    #right phase
    right_mirror = np.fliplr(img[:, -n:rows])
    img_mirror = np.concatenate((img, right_mirror), axis=1)

    #bottom phase
    bottom_mirror = np.flipud(img_mirror[-n:cols, :])
    img_mirror = np.concatenate((img_mirror, bottom_mirror), axis=0)

    return img_mirror

   
################################################################################
# Cuts right and bottom edges of given image.
# @param  img   image to cut
# @param  n     size of border to cut
# @return       cutted image
################################################################################
def cutEdges(img, n):
    return img[:-n, :-n].copy()


################################################################################
# Makes summed area table from given image.
# @param  img image for creating summed area table
# @return     summed area table
################################################################################
def makeSat(img):
  horizontal_phase = np.add.accumulate(img, 1, np.int32)
  vertical_phase = np.add.accumulate(horizontal_phase, 0, np.int32)

  return vertical_phase


################################################################################
# Rolls matrix up and creates paddding with zero padding.
# @param    matrix  matrix for rolling up
# @param    n       size of padding
# @return           matrix with zero padding on bottom
################################################################################
def rollUpPadding(matrix, n):
  return np.concatenate((matrix[n:, :], np.zeros((n, matrix.shape[1]))), axis=0)


################################################################################
# Rolls matrix left and creates paddding with zero padding.
# @param    matrix  matrix for rolling left
# @param    n       size of padding
# @return           matrix with zero padding on right side
################################################################################
def rollLeftPadding(matrix, n):
  return np.concatenate((matrix[:, n:], np.zeros((matrix.shape[0], n))), axis=1) 


################################################################################
# Creates a blurry image using box filter in constant time.
# @param    sat_img summed area table of previously given image
# @param    n       size of kernel
# @return           blurry image
################################################################################
def boxFilter(sat_img, n):
  up = rollUpPadding(sat_img, n)
  left = rollLeftPadding(sat_img, n)
  up_left = rollUpPadding(rollLeftPadding(sat_img, n), n)

  return np.uint8((sat_img + up_left - up - left) * 1.0/(n*n))


################################################################################
# Apply box filter to given image with size of kernel n.
# @param    channel image with one channel of RGB in cvImage format
# @param    n       size of 
# @param    rows    number of rows in image
# @param    cols    number of cols in image
# @return           filtered image with one channel in cvImage format
################################################################################
def applyBoxFilterOneChannel(channel, n, rows, cols):
  feed_mat = cv.GetMat(channel)
  feed_array = np.asmatrix(feed_mat)
  mirror_img = mirrorImage(feed_array, n, rows, cols)
  sat = makeSat(mirror_img)
  filtered_image = boxFilter(sat, n)
  filtered_image = cutEdges(filtered_image, n)
  cv2.putText(filtered_image, str(n), (20,40), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,255,0))
  img = cv.fromarray(filtered_image)

  return img


## MAIN ########################################################################
cv.NamedWindow("webcam", 1)
cam = cv.CaptureFromCAM(-1)

webcam_size = cv.GetSize(cv.QueryFrame(cam))
rows = webcam_size[0]
cols = webcam_size[1]

red = cv.CreateImage(webcam_size, cv.IPL_DEPTH_8U, 1)
green = cv.CreateImage(webcam_size, cv.IPL_DEPTH_8U, 1)
blue = cv.CreateImage(webcam_size, cv.IPL_DEPTH_8U, 1)
merged = cv.CreateImage(webcam_size, cv.IPL_DEPTH_8U, 3)

#size of kernel
n=7

while True:
  feed = cv.QueryFrame(cam)
  cv.Split(feed, red, green, blue, None)

  ## R
  red = applyBoxFilterOneChannel(red, n, rows, cols) #boxfilter
  red = applyBoxFilterOneChannel(red, n, rows, cols) #tent (bartlett)
  red = applyBoxFilterOneChannel(red, n, rows, cols) #gausssian

  ## G
  green = applyBoxFilterOneChannel(green, n, rows, cols) #boxfilter
  green = applyBoxFilterOneChannel(green, n, rows, cols) #tent (bartlett)
  green = applyBoxFilterOneChannel(green, n, rows, cols) #gaussian

  ## B
  blue = applyBoxFilterOneChannel(blue, n, rows, cols) #boxfilter
  blue = applyBoxFilterOneChannel(blue, n, rows, cols) #tent (bartlett)
  blue = applyBoxFilterOneChannel(blue, n, rows, cols) #gaussian

  cv.Merge(red, green, blue, None, merged)
  cv.SaveImage("img.png", merged)
  cv.ShowImage("webcam", merged)

  ## sniffing of keys
  key = chr(cv.WaitKey(1) & 255)

  if key == 'j': #getting larger kernel
    n += 1
    print n
    
  elif key == 'k': #getting smaller kernel
    n -= 1
    if n < 2:
      n = 2

    print n
      
  elif key == 'q': #quit program
    cv.DestroyWindow("webcam")
    break
