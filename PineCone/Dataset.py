from torch.utils.data import Dataset
from torchvision import transforms

import pandas as pd
from PIL import Image


class ClothesDataset(Dataset):
    def __init__(self, dataset_path, dataset_base):
        self.dataset_base = dataset_base
        self.data = pd.read_csv(dataset_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5261, 0.5012, 0.4964], std=[0.3652, 0.3523, 0.3461]),
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        brand = self.data.iloc[idx, 0]
        name = self.data.iloc[idx, 1]
        path = self.data.iloc[idx, 2]
        image = Image.open(self.dataset_base + path).convert("RGB")
        image = self.transform(image).unsqueeze(0)
        return idx, brand, name, image
