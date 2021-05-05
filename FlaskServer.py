#  -------------------------------------------------------------
#   Copyright (c) Microsoft Corporation.  All rights reserved.
#  -------------------------------------------------------------
import os
import io
import re
import base64

from PIL import Image
from flask import Flask, request

from TFClassifier import TFClassifier
from TorchClassifier import TorchClassifier

app = Flask(__name__)

tf_models = {}
torch_models = {}

def get_tf_model(name):
    if not name in tf_models:
        path = os.path.join(".", "Model", name)
        model = TFClassifier(path)
        model.load()
        tf_models[name] = model
    return tf_models[name]

@app.route('/classify/tf/<model_name>', methods=["POST"])
def classify_image_with_tf(model_name):
    req = request.get_json(force=True)
    inputs = req["inputs"]
    image = _process_base64(inputs)
    model = get_tf_model(model_name)
    predictions = model.predict(image)

    # Reformat the TF response into standard Lobe format
    labels = []
    for prediction in predictions["Labels"]:
        labels.append([prediction["label"], prediction["confidence"]])
    bestlabel = labels[0][0]
    result = {"outputs" : {"Labels":labels, "Prediction": [bestlabel]}}

    return result

def get_torch_model(name):
    if not name in torch_models:
        path = os.path.join(".", "model", name+".pt")
        model = TorchClassifier(path)
        model.load()
        torch_models[name] = model
    return torch_models[name]

@app.route('/classify/torch/<model_name>', methods=["POST"])
def classify_image_with_torch(model_name):
    req = request.get_json(force=True)
    inputs = req["inputs"]
    image = _process_base64(inputs)
    model = get_torch_model(model_name)
    result = model.predict(image)
    return result

def _process_base64(json_data):
    image_data = json_data.get("Image")
    image_data = re.sub(r"^data:image/.+;base64,", "", image_data)
    image_base64 = bytearray(image_data, "utf8")
    image = base64.decodebytes(image_base64)
    return Image.open(io.BytesIO(image))

if __name__ == "__main__":
    app.run(host='192.168.0.169', port=38100, debug=True)
