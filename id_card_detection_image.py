
# Import packages
from turtle import color
from utils import visualization_utils as vis_util
from utils import label_map_util
import os
import cv2
import numpy as np
import tensorflow.compat.v1 as tf
import sys

from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites

tf.disable_v2_behavior()
# Name of the directory containing the object detection module we're using
MODEL_NAME = 'model'
IMAGE_NAME = 'test_images/image2.png'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'labelmap.pbtxt')

# Path to image
PATH_TO_IMAGE = os.path.join(CWD_PATH, IMAGE_NAME)

# Number of classes the object detector can identify
NUM_CLASSES = 1

# Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Load image using OpenCV and
# expand image dimensions to have shape: [1, None, None, 3]
# i.e. a single-column array, where each item in the column has the pixel RGB value
image = cv2.imread(PATH_TO_IMAGE)
image_expanded = np.expand_dims(image, axis=0)

# Perform the actual detection by running the model with the image as input
(boxes, scores, classes, num) = sess.run(
    [detection_boxes, detection_scores, detection_classes, num_detections],
    feed_dict={image_tensor: image_expanded})

# Draw the results of the detection (aka 'visulaize the results')
image, array_coord = vis_util.visualize_boxes_and_labels_on_image_array(
    image,
    np.squeeze(boxes),
    np.squeeze(classes).astype(np.int32),
    np.squeeze(scores),
    category_index,
    use_normalized_coordinates=True,
    line_thickness=3,
    min_score_thresh=0.60)

ymin, xmin, ymax, xmax = array_coord

shape = np.shape(image)
im_width, im_height = shape[1], shape[0]
(left, right, top, bottom) = (xmin * im_width,
                              xmax * im_width, ymin * im_height, ymax * im_height)

output_path = "./result.png"
# Using Image to crop and save the extracted copied image
im = cv2.imread(IMAGE_NAME)

im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
im = cv2.GaussianBlur(
    src=im,
    ksize=(3, 3),
    sigmaX=0,
    sigmaY=0)

im = im[int(ymin):int(ymax), int(xmin):int(xmax)]

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
im=clahe.apply(im)

_, im = cv2.threshold(im, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)

cv2.imwrite(output_path, im)

im2 = Image.open(IMAGE_NAME)
im2.crop((left, top, right, bottom)).save(output_path, quality=95)

cv2.imshow('ID-CARD-DETECTOR : ', image)

image_cropped=cv2.imread(output_path)
cv2.imshow("ID-CARD-CROPPED : ", image_cropped)

# All the results have been drawn on image. Now display the image.
cv2.imshow('ID CARD DETECTOR', image)

# Press any key to close the image
cv2.waitKey(0)

# Clean up
cv2.destroyAllWindows()
