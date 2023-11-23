import os
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow import keras
from tensorflow.keras import layers, optimizers
from tensorflow.keras.callbacks import (
    EarlyStopping,
    LearningRateScheduler,
    ModelCheckpoint,
    ReduceLROnPlateau,
    TensorBoard,
)
from tensorflow.keras.layers import (
    LSTM,
    Activation,
    Add,
    BatchNormalization,
    Bidirectional,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    Input,
    Lambda,
    MaxPool2D,
    MaxPooling2D,
    Reshape,
)
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.utils import to_categorical


class CNN_Model(object):
    def __init__(self, weight_path=None):
        self.weight_path = weight_path
        self.model = None

    def build_model(self, rt=False):
        self.model = Sequential()
        self.model.add(
            Conv2D(
                32, (3, 3), padding="same", activation="relu", input_shape=(28, 28, 1)
            )
        )
        self.model.add(Conv2D(32, (3, 3), activation="relu"))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(64, (3, 3), padding="same", activation="relu"))
        self.model.add(Conv2D(64, (3, 3), activation="relu"))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(64, (3, 3), padding="same", activation="relu"))
        self.model.add(Conv2D(64, (3, 3), activation="relu"))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(512, activation="relu"))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(128, activation="relu"))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(2, activation="softmax"))

        if self.weight_path is not None:
            self.model.load_weights(self.weight_path)
        # model.summary()
        if rt:
            return self.model

    @staticmethod
    def load_data():
        dataset_dir = "./datasets/"
        images = []
        labels = []

        for img_path in Path(dataset_dir + "unchoice/").glob("*.png"):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (28, 28), cv2.INTER_AREA)
            img = img.reshape((28, 28, 1))
            label = to_categorical(0, num_classes=2)
            images.append(img / 255.0)
            labels.append(label)

        for img_path in Path(dataset_dir + "choice/").glob("*.png"):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (28, 28), cv2.INTER_AREA)
            img = img.reshape((28, 28, 1))
            label = to_categorical(1, num_classes=2)
            images.append(img / 255.0)
            labels.append(label)

        datasets = list(zip(images, labels))
        np.random.shuffle(datasets)
        images, labels = zip(*datasets)
        images = np.array(images)
        labels = np.array(labels)

        return images, labels

    def train(self):
        images, labels = self.load_data()

        # build model
        self.build_model(rt=False)

        # compile
        self.model.compile(
            loss="categorical_crossentropy",
            optimizer=optimizers.Adam(1e-3),
            metrics=["acc"],
        )

        # reduce learning rate
        reduce_lr = ReduceLROnPlateau(
            monitor="val_acc",
            factor=0.2,
            patience=5,
            verbose=1,
        )

        # Model Checkpoint
        cpt_save = ModelCheckpoint(
            "./weight2.h5", save_best_only=True, monitor="val_acc", mode="max"
        )

        print("Training......")
        self.model.fit(
            images,
            labels,
            callbacks=[cpt_save, reduce_lr],
            verbose=1,
            epochs=10,
            validation_split=0.15,
            batch_size=32,
            shuffle=True,
        )


class CRNN_Model(object):
    def __init__(self, weight_path=None, digit=False, isLSTM=True, isAttention=True):
        self.weight_path = weight_path
        self.model = None
        self.model_CTC = None
        self.isLSTM = isLSTM
        self.isAttention = isAttention
        # self.char_list = None
        # self.max_label_len = None

        if digit:
            self.imgShape = (32, 128, 1)
            self.max_label_len = 10
            self.char_list = "0123456789"
        else:
            self.imgShape = (32, 100, 1)
            self.max_label_len = 24
            self.char_list = " 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvxyzÀÁÂÔÚÝàáâãèéêìíòóôõùúýĂăĐđĩũƒƠơƯưạẢảẤấẦầẩẫậắằẳẵặẹẻẽếỀềỂểễỆệỉịọỏỐốỒồổỗộớờỞởỡợụỦủứừửữựỳỷỹ"

    @staticmethod
    def attention_rnn(inputs):
        # inputs.shape = (batch_size, time_steps, input_dim)
        input_dim = int(inputs.shape[2])
        timestep = int(inputs.shape[1])
        a = layers.Permute((2, 1))(
            inputs
        )  # Permutes the dimensions of the input according to a given pattern.
        a = layers.Dense(timestep, activation="softmax")(
            a
        )  # // Alignment Model + Softmax
        a = layers.Lambda(
            lambda x: keras.backend.mean(x, axis=1), name="dim_reduction"
        )(a)
        a = layers.RepeatVector(input_dim)(a)
        a_probs = layers.Permute((2, 1), name="attention_vec")(a)
        output_attention_mul = layers.multiply(
            [inputs, a_probs], name="attention_mul"
        )  # // Weighted Average
        return output_attention_mul

    # define a ctc lambda function to take arguments and return ctc_bach_cost
    @staticmethod
    def ctc_lambda_func(args):
        y_pred, labels, input_length, label_length = args
        y_pred = y_pred[:, 2:, :]
        return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

    def build_model(self, istrain=False):
        inputs = layers.Input(shape=self.imgShape, name="image", dtype="float32")

        # First conv block
        x = layers.Conv2D(
            64,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv1",
        )(inputs)
        x = layers.MaxPooling2D((2, 2), strides=2, name="pool1")(x)

        # Second conv block
        x = layers.Conv2D(
            128,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv2",
        )(x)
        x = layers.MaxPooling2D((2, 2), strides=2, name="pool2")(x)

        # Third conv block
        x = layers.Conv2D(
            256,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv3",
        )(x)

        # Fourth conv block
        x = layers.Conv2D(
            256,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv4",
        )(x)

        x = layers.MaxPooling2D((2, 1), name="pool4")(x)

        # Fifth conv block
        x = layers.Conv2D(
            512,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv5",
        )(x)

        x = layers.BatchNormalization(momentum=0.8, name="BatchNormalization_1")(x)

        # Sixth conv block
        x = layers.Conv2D(
            512,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv6",
        )(x)

        x = layers.BatchNormalization(momentum=0.8, name="BatchNormalization_2")(x)
        x = layers.MaxPooling2D((2, 1), name="pool6")(x)

        # Seventh conv block
        x = layers.Conv2D(
            512,
            (2, 2),
            activation="relu",
            kernel_initializer="he_normal",
            padding="valid",
            name="Conv7",
        )(x)

        new_shape = (-1, 512)
        x = layers.Reshape(target_shape=new_shape, name="reshape")(x)

        # ----------------------------------------Testing---------------------------------------
        if self.isLSTM:
            x = layers.LSTM(512, return_sequences=True, dropout=0.25)(x)
        # ----------------------------------------Testing---------------------------------------

        # Add attention layer
        if self.isAttention:
            x = self.attention_rnn(x)

        # bidirectional LSTM layers with units=128
        blstm_1 = Bidirectional(LSTM(256, return_sequences=True, dropout=0.2))(x)
        blstm_2 = Bidirectional(LSTM(256, return_sequences=True, dropout=0.2))(blstm_1)

        # this is our softmax character proprobility with timesteps
        outputs = Dense(len(self.char_list) + 1, activation="softmax")(blstm_2)

        # model to be used at test time
        self.model = Model(inputs, outputs)

        # define the label input shape for ctc
        labels = Input(name="the_labels", shape=[self.max_label_len], dtype="float32")

        # define the length of input and label for ctc
        input_length = Input(name="input_length", shape=[1], dtype="int64")
        label_length = Input(name="label_length", shape=[1], dtype="int64")

        # out loss function (just take the inputs and put it in our ctc_batch_cost)
        loss_out = Lambda(self.ctc_lambda_func, output_shape=(1,), name="ctc")(
            [outputs, labels, input_length, label_length]
        )

        # model to be used at training time
        self.model_CTC = Model(
            inputs=[inputs, labels, input_length, label_length], outputs=loss_out
        )

        if self.weight_path is not None:
            if istrain:
                self.model_CTC.load_weights(self.weight_path)
                return self.model_CTC
            else:
                self.model.load_weights(self.weight_path)
                return self.model

    def train(self, train_data, valid_data, epochs, batch_size):
        def lrfn(epoch):
            if epoch <= 10:
                return 1e-3
            elif 10 < epoch <= 20:
                return 1e-4
            elif 20 < epoch <= 30:
                return 1e-5
            elif 30 < epoch <= 40:
                return 1e-6
            else:
                return 1e-8

        # compile the model and return the compiled model
        self.model_CTC.compile(
            loss={"ctc": lambda y_true, y_pred: y_pred}, optimizer="adam"
        )

        # define the callbacks
        callbacks = [
            TensorBoard(
                log_dir="./logs",
                histogram_freq=10,
                profile_batch=0,
                write_graph=True,
                write_images=False,
                update_freq="epoch",
            ),
            ModelCheckpoint(
                filepath=os.path.join("checkpoint_weights.hdf5"),
                monitor="val_loss",
                save_best_only=True,
                save_weights_only=True,
                verbose=1,
            ),
            EarlyStopping(
                monitor="val_loss",
                min_delta=1e-8,
                patience=20,
                restore_best_weights=True,
                verbose=1,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                min_delta=1e-4,  ###### Edited, default 1e-8
                factor=0.2,
                patience=10,
                verbose=1,
            ),
            LearningRateScheduler(lambda epoch: lrfn(epoch), verbose=False),
        ]
        callbacks_list = callbacks

        # train the model
        batch_size = 128
        epochs = 100

        self.model_CTC.fit(
            x=train_data,
            y=np.zeros(len(train_data[0])),
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(valid_data, [np.zeros(len(valid_data[0]))]),
            verbose=1,
            callbacks=callbacks_list,
        )

    @staticmethod
    def preprocess_img(img, imgSize):
        img_batch = []

        widthTarget, heightTarget = imgSize
        height, width = img.shape
        factor_x = width / widthTarget
        factor_y = height / heightTarget
        factor = max(factor_x, factor_y)

        # scale according to factor
        newSize = (
            min(widthTarget, int(width / factor)),
            min(heightTarget, int(height / factor)),
        )
        # print ('newSize ={}, old size = {}'.format(newSize, img.shape ))
        img = cv2.resize(img, newSize)
        target = (
            np.ones(shape=(heightTarget, widthTarget), dtype="uint8") * 255
        )  # tao ma tran 255 (128,32)
        target[0 : newSize[1], 0 : newSize[0]] = img  # Padding trên hoặc dưới

        # transpose
        img = cv2.transpose(target)
        img = cv2.transpose(img)
        # standardization
        mean, stddev = cv2.meanStdDev(img)
        mean = mean[0][0]
        stddev = stddev[0][0]  # standard deviation
        # print ('mean ={}, stddev = {}'.format(mean, stddev))
        img = img - mean
        img = img // (stddev) if stddev > 0 else img

        img = np.expand_dims(img, axis=2)
        img = img / 255.0
        img_batch.append(img)

        img_batch = np.array(img_batch)
        return img_batch

    def num_to_label(self, num):
        ret = ""
        for ch in num:
            if ch == -1:  # CTC Blank
                break
            else:
                ret += self.char_list[ch]
        return ret

    def recognize_name(self, name):
        nameRecognized = str()
        for i in range(len(name)):
            predict_img = self.preprocess_img(name[i], (100, 32))
            preds = self.model.predict(predict_img)
            decoded = tf.keras.backend.get_value(
                tf.keras.backend.ctc_decode(
                    preds,
                    input_length=np.ones(preds.shape[0]) * preds.shape[1],
                    greedy=False,
                    beam_width=5,
                    top_paths=1,
                )[0][0]
            )

            for i in range(len(predict_img)):
                nameRecognized += self.num_to_label(decoded[i]) + " "

        return nameRecognized

    def recognize_digit(self, digit):
        digitRecognized = str()
        predict_img = []
        for i in range(len(digit)):
            predict_img.append(self.preprocess_img(digit[i], (128, 32)) * 255.0)

        predict_img = np.array(predict_img).reshape(-1, 32, 128, 1)

        preds = self.model.predict(predict_img)
        decoded = tf.keras.backend.get_value(
            tf.keras.backend.ctc_decode(
                preds,
                input_length=np.ones(preds.shape[0]) * preds.shape[1],
                greedy=False,
                beam_width=5,
                top_paths=1,
            )[0][0]
        )
        for i in range(len(predict_img)):
            digitRecognized += self.num_to_label(decoded[i])
        return digitRecognized
