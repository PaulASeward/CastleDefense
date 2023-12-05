# from tensorflow.keras.models import Model
# from tensorflow.keras.losses import categorical_crossentropy
# from tensorflow.keras.layers import (
#     Conv1D, Conv2D, MaxPooling1D, MaxPooling2D, AvgPool1D, AvgPool2D, Reshape,
#     Input, Activation, BatchNormalization, Dense, Add, Lambda, Dropout, LayerNormalization)
#
# from tensorflow.keras.optimizers import Adam
# from tensorflow.keras import backend as K
# from tensorflow.keras.callbacks import Callback, EarlyStopping

from keras.losses import categorical_crossentropy
from keras.models import Model

from keras.layers import (
    Conv1D, Conv2D, MaxPooling1D, MaxPooling2D, AvgPool1D, AvgPool2D, Reshape,
    Input, Activation, BatchNormalization, Dense, Add, Lambda, Dropout, LayerNormalization)

from keras.optimizers import Adam
from keras import backend as K
from keras.callbacks import Callback, EarlyStopping

import numpy as np
import pandas as pd
import keras
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold


def get_conv_net(num_classes_y=11):
    # _, x, y, z = train_x.shape
    inputdense_players = Input(shape=(11, 10, 10), name="playersfeatures_input")

    X = Conv2D(128, kernel_size=(1, 1), strides=(1, 1), activation='relu')(inputdense_players)
    X = Conv2D(160, kernel_size=(1, 1), strides=(1, 1), activation='relu')(X)
    X = Conv2D(128, kernel_size=(1, 1), strides=(1, 1), activation='relu')(X)

    # The second block of convolutions learns the necessary information per defense player before the aggregation.
    # For this reason the pool_size should be (1, 10). If you want to learn per off player the pool_size must be
    # (11, 1)
    Xmax = MaxPooling2D(pool_size=(1, 10))(X)
    Xmax = Lambda(lambda x1: x1 * 0.3)(Xmax)

    Xavg = AvgPool2D(pool_size=(1, 10))(X)
    Xavg = Lambda(lambda x1: x1 * 0.7)(Xavg)

    X = Add()([Xmax, Xavg])
    X = Lambda(lambda y: K.squeeze(y, 2))(X)
    X = BatchNormalization()(X)

    X = Conv1D(160, kernel_size=1, strides=1, activation='relu')(X)
    X = BatchNormalization()(X)
    X = Conv1D(96, kernel_size=1, strides=1, activation='relu')(X)
    X = BatchNormalization()(X)
    X = Conv1D(96, kernel_size=1, strides=1, activation='relu')(X)
    X = BatchNormalization()(X)

    Xmax = MaxPooling1D(pool_size=11)(X)
    Xmax = Lambda(lambda x1: x1 * 0.3)(Xmax)

    Xavg = AvgPool1D(pool_size=11)(X)
    Xavg = Lambda(lambda x1: x1 * 0.7)(Xavg)

    X = Add()([Xmax, Xavg])
    X = Lambda(lambda y: K.squeeze(y, 1))(X)

    X = Dense(96, activation="relu")(X)
    X = BatchNormalization()(X)

    X = Dense(256, activation="relu")(X)
    X = LayerNormalization()(X)
    X = Dropout(0.3)(X)

    outsoft = Dense(11, activation='softmax', name="output")(X)

    model = Model(inputs=[inputdense_players], outputs=outsoft)
    return model


# class Metric(Callback):
#     def __init__(self, model, callbacks, data):
#         super().__init__()
#         self.model = model
#         self.callbacks = callbacks
#         self.data = data
#
#     def on_train_begin(self, logs=None):
#         for callback in self.callbacks:
#             callback.on_train_begin(logs)
#
#     def on_train_end(self, logs=None):
#         for callback in self.callbacks:
#             callback.on_train_end(logs)
#
#     def on_epoch_end(self, batch, logs=None):
#         X_valid, y_valid = self.data[0], self.data[1]
#
#         y_pred = self.model.predict(X_valid)
#         y_true = np.clip(np.cumsum(y_valid, axis=1), 0, 1)
#         y_pred = np.clip(np.cumsum(y_pred, axis=1), 0, 1)
#         val_s = ((y_true - y_pred) ** 2).sum(axis=1).sum(axis=0) / (199 * X_valid.shape[0])
#         logs['val_CRPS'] = val_s
#
#         y_pred = self.model.predict(X_valid)
#         y_true = np.zeros_like(y_pred)
#         y_true[np.arange(y_true.shape[0]), np.argmax(y_valid, axis=1)] = 1
#
#         val_loss = CategoricalCrossentropy()(y_true, y_pred).numpy()
#
#
#         for callback in self.callbacks:
#             callback.on_epoch_end(batch, logs)


def train_model(train_x, train_y, num_classes_y=11):
    models = []
    kf = KFold(n_splits=8, shuffle=True, random_state=42)
    scores = []

    for i, (tdx, vdx) in enumerate(kf.split(train_x, train_y)):
        print(f'Fold : {i}')
        X_train, X_val = train_x[tdx], train_x[vdx]
        y_train, y_val = train_y[tdx], train_y[vdx]

        # Convert y_train and y_val to one-hot encoded format
        y_train_onehot = keras.utils.to_categorical(y_train, num_classes=num_classes_y)
        y_val_onehot = keras.utils.to_categorical(y_val, num_classes=num_classes_y)

        # y_train_values = np.zeros((len(y_train), num_classes_y), np.int32)
        # for irow, row in enumerate(y_train):
        #     y_train_values[(irow, row - min_idx_y)] = 1
        #
        # y_val_values = np.zeros((len(y_val), num_classes_y), np.int32)
        # for irow, row in enumerate(y_val - min_idx_y):
        #     y_val_values[(irow, row)] = 1

        #
        # y_train_values = y_train_values.astype('float32')
        # y_val_values = y_val_values.astype('float32')

        model = get_conv_net(num_classes_y)

        es = EarlyStopping(monitor='val_loss',
                           mode='min',
                           restore_best_weights=True,
                           verbose=1,
                           patience=10)
        #
        # es.set_model(model)
        # metric = Metric(model, [es], [X_val, y_val_values])

        lr_i = 1e-3
        lr_f = 5e-4
        n_epochs = 50

        decay = (1 - lr_f / lr_i) / ((lr_f / lr_i) * n_epochs - 1)  # Time-based decay formula
        alpha = (lr_i * (1 + decay))

        opt = Adam(learning_rate=1e-3)

        model.compile(loss=categorical_crossentropy,
                      optimizer=opt, metrics=['accuracy'])

        history = model.fit(X_train,
                            y_train_onehot,
                            epochs=n_epochs,
                            batch_size=64,
                            verbose=1,
                            validation_data=(X_val, y_val_onehot),
                            callbacks=[es])

        # Get the best validation loss and accuracy from the history
        best_val_loss = min(history.history['val_loss'])
        best_val_accuracy = max(history.history['val_accuracy'])
        print(f"Best Val Loss: {best_val_loss}")
        print(f"Best Val Accuracy: {best_val_accuracy}")

        scores.append((best_val_loss, best_val_accuracy))

        models.append(model)

    # Calculate the average of the validation scores
    avg_val_loss = np.mean([score[0] for score in scores])
    avg_val_accuracy = np.mean([score[1] for score in scores])
    print(f"Average Val Loss: {avg_val_loss}")
    print(f"Average Val Accuracy: {avg_val_accuracy}")

    return models


train_x = np.load('processed_data/train_x_v0.npy')
print('Train_x Shape: ', train_x.shape)
train_y = np.load('processed_data/train_y_v0.npy')
# train_y = pd.read_pickle('processed_data/train_y_v0.pkl')
print('Train_y Shape: ',train_y.shape)
# train_model(train_x, train_y, num_classes_y=11)