import tensorflow as tf

from math import sqrt

def visualize_feature(layer):
    """This function puts the layer outputs into images stacked vertically.
    Args:
        layer: tensor of shape [Y, X, NumChannels, NumKernels] (HWCN)
    Return:
        flattened tensor
    """
    features = tf.unstack(layer, axis=3)
    layer_max = tf.reduce_max(layer)
    features_padded = list(map(lambda t: tf.pad(t-layer_max,[[0,0], [0,1], [0,0]]) + layer_max, features))
    imgs = tf.expand_dims(tf.concat(features_padded, 1), -1)
    return imgs

def visualize_filter(kernel, pad=1, name='visualizer'):
    """Visualize convolutional filters as an image.
    Arranges filters into a grid, with some paddings between adjacent filters.
    Args:
        kernel:            tensor of shape [Y, X, NumChannels, NumKernels] (HWCN)
        pad:               number of black pixels around each filter (between them)
        name:              name for tensorflow scope
    Return:
        Tensor of shape [1, (Y+2*pad)*grid_Y, (X+2*pad)*grid_X, NumChannels].
    Notes:
        This was originally written by kukurza and was adapted for this tutorial.
        https://gist.github.com/kukuruza/03731dc494603ceab0c5    
    """
    with tf.variable_scope(name) as scope:

        def factorization(n):
            for i in range(int(sqrt(float(n))), 0, -1):
                if n % i == 0:
                    if i == 1: print('Who would enter a prime number of filters')
                    return (i, int(n / i))
        (grid_Y, grid_X) = factorization (kernel.get_shape()[3].value)

        x_min = tf.reduce_min(kernel)
        x_max = tf.reduce_max(kernel)

        kernel1 = (kernel - x_min) / (x_max - x_min)

        # pad X and Y
        x1 = tf.pad(kernel1, tf.constant( [[pad,pad],[pad, pad],[0,0],[0,0]] ), mode = 'CONSTANT')

        # X and Y dimensions, w.r.t. padding
        Y = kernel1.get_shape()[0] + 2 * pad
        X = kernel1.get_shape()[1] + 2 * pad

        channels = kernel1.get_shape()[2]

        # put NumKernels to the 1st dimension
        x2 = tf.transpose(x1, (3, 0, 1, 2))
        # organize grid on Y axis
        x3 = tf.reshape(x2, tf.stack([grid_X, Y * grid_Y, X, channels])) #3

        # switch X and Y axes
        x4 = tf.transpose(x3, (0, 2, 1, 3))
        # organize grid on X axis
        x5 = tf.reshape(x4, tf.stack([1, X * grid_X, Y * grid_Y, channels])) #3

        # back to normal order (not combining with the next step for clarity)
        x6 = tf.transpose(x5, (2, 1, 3, 0))

        # to tf.image_summary order [batch_size, height, width, channels],
        #   where in this case batch_size == 1
        x7 = tf.transpose(x6, (3, 0, 1, 2))
        
        # handle multi-channel filters
        if channels > 1:
            features = tf.unstack(x7,axis=3)
            features_max = tf.reduce_max(features)
            features_padded = list(map(lambda t: tf.pad(t-features_max, [[0,0],[0,1],[0,0]])+features_max,features))
            x7 = tf.expand_dims(tf.concat(features_padded,1),-1)
            
        # scale to [0, 255] and convert to uint8
        imgs = tf.image.convert_image_dtype(x7, dtype = tf.uint8)
    return imgs
