from CastleDefense.data_analysis.create_tensor import create_tensor_train_x

import os
import keras
from keras import backend as K
from keras.models import load_model


# loaded_model = load_model(checkpoint_filepath, compile=False, custom_objects={'<lambda>': lambda x: x}, safe_mode=False)


def use_model_to_predict_tackler(tracking_data):
    i = 0
    checkpoint_filepath = f'best_model_fold_{i}.h5'
    checkpoint_filepath = os.path.join('processed_data', 'models', checkpoint_filepath)

    loaded_model = keras.models.load_model(checkpoint_filepath)

    x_train = create_tensor_train_x(tracking_data)
    y_pred = loaded_model.predict(x_train)
    # TODO: Run through debugger to check y_pred values mmake reasonable sense to amke sure indexes are consistent.

    return x_train, y_pred