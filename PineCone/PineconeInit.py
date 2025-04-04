import os
from dotenv import load_dotenv # Petr Tarasov Daun

from Dataset import ClothesDataset

import torch
from torch.utils.data import DataLoader
import torch.multiprocessing as mp

from tqdm import tqdm

from EmbeddingModel import ResNetEmbedding

from pinecone import Pinecone, ServerlessSpec

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
DATASET_PATH = os.getenv("DATASET_PATH")
WEIGHTS_PATH = os.getenv("WEIGHTS_PATH")

pc = Pinecone(api_key=API_KEY)

mp.set_start_method('fork', force=True)
dataset = ClothesDataset(DATASET_PATH, r"parsers/dataset/")
loader = DataLoader(dataset, batch_size=16, shuffle=False, num_workers=3)

device = torch.device("mps")
embedding_model = ResNetEmbedding()
checkpoint = torch.load(WEIGHTS_PATH, map_location=device)
embedding_model.load_state_dict(checkpoint["model_state_dict"])
embedding_model.to(device)
embedding_model.eval()

index = pc.Index("clothes-images-2")

progress_bar = tqdm(loader, desc="Buildimg embeddings")
for batch in progress_bar:
    vectors = []
    for idx, brand, name, image in zip(*batch):
        image = image.to(device)
        embedding = embedding_model(image).cpu().detach().numpy()
        vectors.append({
            "id": str(idx.item()),
            "values": embedding.tolist()[0],
            "metadata": {"brand": brand, "name": name, "image": image.tolist()[0]}
        })
    index.upsert(vectors=vectors, namespace="clothes-images-2")

