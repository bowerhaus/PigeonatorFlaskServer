import torch
import time
from detecto.core import DataLoader, Model

model = Model(['Pigeon'])

class DetectoDetector:
    
    def __init__(self, model_name):
        self.name = model_name

    def load(self):
        self.model = Model.load(self.name, ['Pigeon'])

    def predict(self, image):
        start_time = int(time.time()*1000)
        labels, boxes, scores = self.model.predict(image)
        end_time = int(time.time()*1000)
        items = []
        for i in range(len(labels)):
           items.append({"label": labels[i], "score": scores[i].item(), "box": boxes[i].numpy().tolist()})
        return {"outputs": {"Items": items, "Elapsed": end_time-start_time}}