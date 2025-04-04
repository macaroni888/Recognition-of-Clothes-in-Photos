import torch.nn as nn
from torch import load
from torchvision import models
from torch.utils.data import Dataset
from torchvision import transforms

from PIL import Image


class ResNetEmbedding(nn.Module):
    def __init__(self, embedding_dim=128, name="embedding_model"):
        super(ResNetEmbedding, self).__init__()
        self.resnet = models.resnet50(weights=None)
        self.resnet.fc = nn.Linear(2048, embedding_dim)
        self.name = name

    def forward(self, x):
        return self.resnet(x)


def load_embedding_model(weights_path, device):
    embedding_model = ResNetEmbedding()
    checkpoint = load(weights_path, map_location=device)
    embedding_model.load_state_dict(checkpoint["model_state_dict"])
    embedding_model.to(device)
    return embedding_model


def make_embedding(embedding_model, img_path, device):
    embedding_model.eval()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image = Image.open(img_path).convert("RGB")
    image = transform(image).unsqueeze(0)
    image = image.to(device)
    embedding = embedding_model(image).cpu().detach().numpy()
    return embedding.tolist()[0]
