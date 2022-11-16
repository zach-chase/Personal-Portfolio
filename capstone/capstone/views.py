from django.shortcuts import render
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from pathlib import Path
from django.core.files.storage import default_storage
from django.conf import settings 
from tensorflow.python.keras.backend import set_session
from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
from keras.applications.imagenet_utils import decode_predictions
import matplotlib.pyplot as plt
import numpy as np
import keras
import tensorflow as tf
from keras.applications import vgg16
import os
import datetime
import traceback
from dask.array.image import imread
from skimage import color, io
import cv2

possible_behaviors = ["Safe Driving",
"Texting - Right",
"Talking on the Phone - Right",
"Texting - Left",
"Talking on the Phone - Left",
"Operating the Radio",
"Drinking",
"Reaching Behind",
"Hair and Makeup",
"Talking to Passenger" ]

def index(request):
    if  request.method == "POST":
        f=request.FILES['sentFile'] # here you get the files needed
        response = {}
        file_name = "pic.jpg"
        file_name_2 = default_storage.save(file_name, f)
        file_url = default_storage.url(file_name_2)

        # File location
        #file_url = os.getcwd() + "/capstone/media/pic.jpg"
        BASE_DIR = Path(__file__).resolve().parent.parent
        MEDIA_ROOT = os.path.join(BASE_DIR, 'media/' + file_name_2)
        original = load_img(MEDIA_ROOT, target_size=(224, 224))
        #original = load_img(f, target_size=(224, 224))
        numpy_image = img_to_array(original)

        current_image = color.rgb2gray(original)
        current_image = cv2.resize(current_image,(224,224))
        current_image = np.array(current_image).reshape(-1,224,224,1)

        image_batch = np.expand_dims(current_image, axis=0)
        #image_batch = np.expand_dims(numpy_image, axis=0)
        # prepare the image for the VGG model
        #processed_image = vgg16.preprocess_input(image_batch.copy())
        processed_image = image_batch
        
        # get the predicted probabilities for each class
        with settings.GRAPH1.as_default():
            session = keras.backend.get_session()
            init = tf.compat.v1.global_variables_initializer()
            session.run(init)
            set_session(settings.SESS)
            predictions=settings.VGG_MODEL.predict(current_image)
       
        #label = decode_predictions(predictions)
        label = predictions
        label = list(label)[0]

        index = np.argmax(label)


        results = [[b, str(float("{:.2f}".format(float(p*100)))) + "%"] for b, p in zip(possible_behaviors, label)]

        #response['percents'] = label
        #response['outcomes'] = possible_behaviors
        response['answer'] = results
        response['main_guess'] = possible_behaviors[index]
        response['main_percent'] = str(float("{:.2f}".format(float(label[index]*100)))) + "%"
        response['guess'] = [possible_behaviors[index], str(float("{:.2f}".format(float(label[index]*100)))) + "%"]
        response['image'] = 'media/' + file_name_2

# <img src="media/pic.jpg">

        return render(request,'results.html',response)
    else:
        return render(request,'start.html')