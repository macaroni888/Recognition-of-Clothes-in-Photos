import torch.nn as nn
from torchvision import models


class ResNetEmbedding(nn.Module):
    def __init__(self, embedding_dim=128, name="embedding_model"):
        super(ResNetEmbedding, self).__init__()
        self.resnet = models.resnet50(weights=None)
        self.resnet.fc = nn.Linear(2048, embedding_dim)
        self.name = name

    def forward(self, x):
        return self.resnet(x)
