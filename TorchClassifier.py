import torchvision
import torch
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import torchvision.models as models
from PIL import Image

class TorchClassifier:
    
    def __init__(self, model_name):
        self.name = model_name
        self.device = "cpu"

    def load(self):
        self.resnet18 = torch.load(self.name).to(self.device)
        self.resnet18.eval()

    def predict(self, image):
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])
        transform = transforms.Compose([transforms.Resize(255),
                                transforms.ToTensor(),
                                normalize])

        ready_image = transform(image).unsqueeze(0)
        output = self.resnet18(ready_image)
        probs = torch.nn.functional.softmax(output,1)
        probslist = probs.detach().numpy().tolist()[0]

        labels = [["None", probslist[0]], ["Pigeon", probslist[1]]]
        sorted_labels = sorted(labels, key=lambda k: k[1], reverse=True)
        bestlabel = sorted_labels[0][0]

        result = {"outputs" : {"Labels":sorted_labels, "Prediction": [bestlabel]}}
        return result

