"""Preprocess image to the HTR model"""

import tensorflow.image as tf_image
import tensorflow.keras.preprocessing.sequence as sequence
import tensorflow.keras.preprocessing.image as keras_image
import numpy as np
import cv2


def process_image(img_path, nb_features):
    """Make the process with the nb_features to the scale resize"""

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = remove_cursive_style(img)

    img = np.reshape(img, img.shape + (1,))
    img = tf_image.per_image_standardization(img)
    img = tf_image.resize(img, size=(nb_features, 3500), preserve_aspect_ratio=True, antialias=True)
    img = tf_image.rot90(img, k=3)[:,:,0]

    # cv2.imshow("img", keras_image.img_to_array(img))
    # cv2.waitKey(0)
    return img


def padding_list(inputs, value):
    """Fill lists with pad value"""

    return sequence.pad_sequences(inputs, value=float(value), dtype="float32", padding="post", truncating="post")


def remove_cursive_style(img):
    """Remove cursive writing style from image with deslanting algorithm"""

    def calc_y_alpha(vec):
        indices = np.where(vec > 0)[0]
        h_alpha = len(indices)

        if h_alpha > 0:
            delta_y_alpha = indices[h_alpha - 1] - indices[0] + 1

            if h_alpha == delta_y_alpha:
                return h_alpha * h_alpha
        return 0

    _, otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    rows, cols = otsu.shape
    alpha_vals = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    results = []

    for alpha in alpha_vals:
        shift_x = max(-alpha * rows, 0.)
        size = (cols + int(np.ceil(abs(alpha * rows))), rows)
        transform = np.array([[1, alpha, shift_x], [0, 1, 0]], dtype=np.float)

        shear_img = cv2.warpAffine(otsu, transform, size, cv2.INTER_NEAREST)
        sum_alpha = 0
        sum_alpha += np.apply_along_axis(calc_y_alpha, 0, shear_img)
        results.append([np.sum(sum_alpha), size, transform])

    result = sorted(results, key=lambda x: x[0], reverse=True)[0]
    return cv2.warpAffine(img, result[2], result[1], borderValue=255)
