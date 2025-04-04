from Embedding.EmbeddingModel import load_embedding_model, make_embedding
from PineCone.Dataset import ClothesDataset

from pinecone import Pinecone

import os
from dotenv import load_dotenv

import torch
import numpy as np
from PIL import Image


def denormalize(image_tensor):
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    image_tensor = image_tensor * std + mean
    image_tensor = torch.clamp(image_tensor, 0, 1)
    image_array = (image_tensor.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
    return Image.fromarray(image_array)


def search(paths_to_images, answer_path):
    load_dotenv()

    API_KEY = os.getenv("PINECONE_API_KEY")
    WEIGHTS_PATH = os.getenv("WEIGHTS_PATH")
    DATASET_PATH = os.getenv("DATASET_PATH")

    device = torch.device("mps")

    dataset = ClothesDataset(DATASET_PATH, r"parsers/dataset/")
    embedding_model = load_embedding_model(WEIGHTS_PATH, device)
    embedding_model.eval()

    pc = Pinecone(api_key=API_KEY)
    index = pc.Index("clothes-images")

    for path in paths_to_images:
        embedding = make_embedding(embedding_model, path)
        results = index.query(
            namespace="clothes-images",
            vector=embedding,
            top_k=5,
            include_metadata=True,
            include_values=False
        )
        for i, res in enumerate(results):
            idx = int(res["id"])
            metadata = res["metadata"]
            brand = metadata["brand"]
            name = metadata["name"]

            _, _, _, found_image = dataset[idx]

            found_image = found_image.squeeze(0)
            found_image = denormalize(found_image)

            saving_dir = os.path.join(answer_path, f"result_{i + 1}")
            os.makedirs(saving_dir, exist_ok=True)
            found_image_path = os.path.join(saving_dir, f"{brand}_{name}")
            found_image.save(found_image_path)
