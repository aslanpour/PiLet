import os
import cv2
import numpy as np
from flask import Flask, render_template, request, json
from waitress import serve
import requests
import datetime
#from PIL import Image
from io import BytesIO

app = Flask(__name__)

INPUT_MODEL_WEIGHTS = "/usr/python/yolov3-tiny.weights"
INPUT_MODEL_CONFIG = "/usr/python/yolov3-tiny.cfg"
INPUT_MODEL_CLASSES = "/usr/python/yolov3-tiny.txt"

ROOT_DIR = os.path.abspath("/")
MODEL_WEIGHTS_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_WEIGHTS)
MODEL_CONFIG_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_CONFIG)
MODEL_CLASSES_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_CLASSES)

with open(MODEL_CLASSES_PATH, 'r') as f:
        classes = [line.strip() for line in f.readlines()]

np.random.seed(42)
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet(MODEL_WEIGHTS_PATH, MODEL_CONFIG_PATH)

def get_output_layers(net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers

#Either receives a header as IMAGE-API or a file attached as image_file
@app.route('/', methods=['POST','PUT','GET'])
def upload_file():
        start=datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        # #if Image-API in header, it should request the file from object storage
        if request.headers.get('Image-API'):

                IMAGE_API = str(request.headers.get('Image-API'))
                #url = "http://10.76.7.91:5000/pioss/api/read/pic_41.jpg"
                url=IMAGE_API
                r = requests.get(url)

                # save on disk as file_name
                with open("image.jpg", "wb") as f:
                        f.write(r.content)
                # read from disk
                file = open("image.jpg", 'rb')

        #otherwise, the file is received along with the incoming request
        else:
                file = request.files['image_file']

        image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        Width = image.shape[1]
        Height = image.shape[0]

        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416,416), (0,0,0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(get_output_layers(net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.4
        nms_threshold = 0.3

        for out in outs:
                for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]
                        if confidence > conf_threshold :
                                class_ids.append(class_id)
                                confidences.append(float(confidence))

        output = ""
        for i in range(0,len(class_ids)):
                output = output + "Class: " + classes[class_ids[i]] + " with confidence: " + str(confidences[i]) + "\n"
        if output =="":
                output="No Object"

        #response = flask.Response()

        response = app.response_class(response=json.dumps(output),
                                      status=200,
                                      mimetype='application/json')
        #response.headers['Detected-Objects'] = output.strip()
        response.headers['Sensor-ID'] = str(request.headers.get('Sensor-ID'))
        end=datetime.datetime.now(datetime.timezone.utc).astimezone().timestamp()
        elapsed = end- start
        response.headers['Exec-Time'] = str(elapsed)
        # it already makes a header as X-Duration-Seconds
        return response

@app.route('/test', methods=['POST','PUT','GET'])
def test():
        return "Test Success"

if __name__ == '__main__':
        #app.run()
	serve(app, host='0.0.0.0', port=5000)
