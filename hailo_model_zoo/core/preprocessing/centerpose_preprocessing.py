import tensorflow as tf
import cv2
import numpy as np
from hailo_model_zoo.core.preprocessing.affine_utils import get_affine_transform


def _centerpose_preprocessing(image, height, width):
    image = np.array(image)
    height, width = int(height), int(width)
    current_height, current_width = image.shape[0:2]

    center = np.array([current_width / 2., current_height / 2.], dtype=np.float32)
    scale = float(max(current_height, current_width))

    trans_input = get_affine_transform(center, scale, 0, [width, height])
    inp_image = cv2.warpAffine(
        image, trans_input, (width, height),
        flags=cv2.INTER_LINEAR)

    return inp_image, center, scale


def centerpose_preprocessing(image, image_info=None, height=None, width=None, **kwargs):
    image_info['orig_height'], image_info['orig_width'] = tf.shape(image)[0], tf.shape(image)[1]
    image_info['img_orig'] = tf.image.encode_jpeg(image, quality=100)
    image, center, scale = tf.compat.v1.py_function(_centerpose_preprocessing,
                                                    [image, height, width],
                                                    [tf.float32, tf.float32, tf.float32])
    image.set_shape((height, width, 3))
    image_info['img_resized'] = image
    image_info['center'], image_info['scale'] = center, scale

    return image, image_info
