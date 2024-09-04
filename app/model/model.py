# import tensorflow as tf
# import numpy as np

# from keras.api.utils import load_img, img_to_array


# model_path = 'app/model/vgg19_model_02.h5'
# model = tf.keras.models.load_model(model_path)

# classes = ['Normal', 'Pneumonia']

# def preprocess_image(img_path, img_size=(128, 128)):
#     img = load_img(img_path, target_size=img_size)
#     img_array = img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0)  # Expand dimensions to match batch size used during training
#     predicts = model.predict(img_array)
#     predict = predicts[0][0]
#     return predict

