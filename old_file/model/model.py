import logging, os
logging.disable(logging.WARNING)
# logging.getLogger('tensorflow').disabled = True
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
import cv2
import keras.backend as K
import numpy as np
from tensorflow import keras
from keras import layers
from keras.layers import (
    LSTM,
    Activation,
    Add,
    BatchNormalization,
    Bidirectional,
    Conv2D,
    Dense,
    Dropout,
    MaxPool2D,
    Reshape,
)
from keras.models import Model
from PIL import Image, ImageTk

class CRNN_Model(object):
    def __init__(self, weight_path=None):
        self.weight_path = weight_path
        self.model = None
        self.model_CTC = None

        self.imgShape = (60,1280,1)
        self.max_label_len = 158
        self.char_list = " #'()+,-./0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYabcdeghiklmnopqrstuvwxyzÂÊÔàáâãèéêìíòóôõùúýăĐđĩũƠơưạảấầẩậắằẵặẻẽếềểễệỉịọỏốồổỗộớờởỡợụủỨứừửữựỳỵỷỹ"

    # define a ctc lambda function to take arguments and return ctc_bach_cost
    @staticmethod
    def ctc_lambda_func(args):
        y_pred, labels, input_length, label_length = args
        y_pred = y_pred[:, 2:, :]
        return K.ctc_batch_cost(labels, y_pred, input_length, label_length)

    def build_model(self):
        inputs = layers.Input(shape=self.imgShape, name="image", dtype="float32")

        # Block 1
        x = Conv2D(64, (3,3), padding='same')(inputs)
        x = MaxPool2D(pool_size=(2, 2))(x)
        x = Activation('relu')(x)
        x_1 = x

        # Block 2
        x = Conv2D(128, (3,3), padding='same')(x)
        x = MaxPool2D(pool_size=(2, 2))(x)
        x = Activation('relu')(x)
        x_2 = x

        # Block 3
        x = Conv2D(256, (3,3), padding='same')(x)
        x = BatchNormalization()(x)
        x = MaxPool2D(pool_size=(2, 2))(x)
        x = Activation('relu')(x)
        x_3 = x

        # Block4
        x = Conv2D(256, (3,3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Add()([x,x_3])
        x = Activation('relu')(x)
        x_4 = x

        # Block5
        x = Conv2D(512, (3,3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x_5 = x

        # Block6
        x = Conv2D(512, (3,3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Add()([x,x_5])
        x = MaxPool2D(pool_size=(2, 1))(x)
        x = Activation('relu')(x)

        # Block7
        x = Conv2D(512, (3,3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        # pooling layer with kernel size (2,2) to make the height/2 #(1,9,512)
        x = MaxPool2D(pool_size=(2, 1))(x)

        # # to remove the first dimension of one: (1, 31, 512) to (31, 512)
        # x = Lambda(lambda x: K.squeeze(x, 1))(x)

        new_shape = int(x.shape[2]), -1
        x = Reshape(target_shape=new_shape, name="reshape")(x)

        x = Dense(512, activation='relu', kernel_initializer='he_normal', name='dense1')(x) 
        x = Dropout(0.25)(x) 
        # x = attention_rnn(x)

        # # # bidirectional LSTM layers with units=128
        blstm_1 = Bidirectional(LSTM(256, return_sequences=True, dropout = 0.2))(x)
        blstm_2 = Bidirectional(LSTM(256, return_sequences=True, dropout = 0.2))(blstm_1)

        # # this is our softmax character proprobility with timesteps
        outputs = Dense(len(self.char_list) + 1, activation = 'softmax')(blstm_2)

        # model to be used at test time
        self.model = Model(inputs, outputs)

        # if self.weight_path is not None:
        self.model.load_weights(self.weight_path)
        return self.model
            

    @staticmethod
    def preprocess_img(img, input_shape):
        img_batch = []
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        
        height, width = img.shape
        img = cv2.resize(img, (int(input_shape[0] / height * width), input_shape[0]))
        height, width = img.shape

        img = np.pad(img, ((0, 0), (0, input_shape[1] - width)), "median")

        img = cv2.GaussianBlur(img, (5, 5), 0)
        img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4
        )

        # img = cv2.transpose(img)
        img = np.expand_dims(img, axis=2)
        img = img / 255.0
        img_batch.append(img)

        img_batch = np.array(img_batch)
        return img_batch

    def num_to_label(self, num):
        pred = ""
        for p in num:
            if int(p) != -1:
                pred += self.char_list[int(p)]
        return pred

    def recognize(self, image):
        stringRecognized = str()
        predict_img = self.preprocess_img(image, (60, 1280))
        prediction = self.model.predict(predict_img)
        out = K.get_value(
            K.ctc_decode(
                prediction,
                input_length=np.ones(prediction.shape[0]) * prediction.shape[1],
                greedy=True,
            )[0][0]
        )

        for x in out:
            stringRecognized += self.num_to_label(x)

        return stringRecognized

# path = "model/train1.hdf5"
# ocr = CRNN_Model(path)
# ocr.build_model()
# img = Image.open("Untitled21.png")
# string_aa = ocr.recognize(img)
# print(string_aa)
