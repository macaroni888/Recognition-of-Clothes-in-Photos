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


class ApplyToNonWhite:
    def __init__(self, threshold=1.0):
        self.threshold = threshold

        self.resize = transforms.Resize((224, 224))
        self.to_tensor = transforms.ToTensor()

        mean = [0.5261, 0.5012, 0.4964]
        std = [0.3652, 0.3523, 0.3461]
        self.normalize = transforms.Normalize(mean=mean, std=std)

    def __call__(self, img):
        cropped = self.resize(img)
        cropped = self.to_tensor(cropped)

        mask = (cropped < self.threshold).any(dim=0)

        aug_img = cropped.clone()
        aug_img = self.normalize(aug_img)

        out = cropped.clone()
        for c in range(3):
            out[c][mask] = aug_img[c][mask]

        return out


def load_embedding_model(weights_path, device):
    embedding_model = ResNetEmbedding(256)
    checkpoint = load(weights_path, map_location=device)
    embedding_model.load_state_dict(checkpoint["model_state_dict"])
    embedding_model.to(device)
    return embedding_model


def make_embedding(embedding_model, img_path, device):
    embedding_model.eval()
    transform = ApplyToNonWhite()

    image = Image.open(img_path).convert("RGB")
    image = transform(image).unsqueeze(0)
    image = image.to(device)
    embedding = embedding_model(image).cpu().detach().numpy()
    return embedding.tolist()[0]
