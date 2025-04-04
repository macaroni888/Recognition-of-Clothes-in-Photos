import torch
from torchvision.transforms import v2 as T
import numpy as np
import cv2
import os
from PIL import Image
import model
from torchvision.io import read_image


def get_transform_vis():
    transforms = []
    transforms.append(T.Resize((512, 512)))
    transforms.append(T.ToDtype(torch.float, scale=True))
    transforms.append(T.ToPureTensor())
    return T.Compose(transforms)


names = ['pants', 'jacked', 'sweater', 't-shirt', 'bodysuit', 'bra', 'dress', 'intimate', 'panties', 'romper', 'shorts',
         'skirt', 'suit', 'swimwear', 'shirt']


def get_masks(image, prediction, output_dir, th_mask=0.5, th_box=0.3):
    masks = torch.squeeze(prediction[0]['masks']).cpu()
    labels = torch.squeeze(prediction[0]['labels']).cpu()
    scores = torch.squeeze(prediction[0]['scores']).cpu()
    boxes = torch.squeeze(prediction[0]['boxes']).cpu()

    threshold = torch.Tensor([th_mask])
    masks = (masks > threshold).bool()

    for i in range(len(masks)):
        if scores[i] < th_box:
            continue

        if labels[i] == 1:
            continue

        x1, y1, x2, y2 = map(int, boxes[i])
        mask_bbox = masks[i][y1:y2, x1:x2]

        segmented = np.ones((y2-y1, x2-x1, 3), dtype=np.uint8) * 255
        segmented[mask_bbox] = image[y1:y2, x1:x2][mask_bbox]

        class_name = names[labels[i] - 2]
        filename = f"{output_dir}/{class_name}_{i}.png"

        cv2.imwrite(filename, cv2.cvtColor(segmented, cv2.COLOR_RGB2BGR))

    print(f"Сохранено в {output_dir}")


def get_segm(path_input, output_directory):
    device = torch.device('cpu')
    model_v4 = model.get_model_v4(num_classes=17)
    checkpoint = torch.load('./models/mask-rcnn-6-29.pth', map_location=device)

    model_v4.load_state_dict(checkpoint['model_state_dict'])
    model_v4.to(device)
    model_v4.eval()

    to_tensor = get_transform_vis()
    image_upload = read_image(path_input)
    image = to_tensor(image_upload)

    image_upload_2 = Image.open(path_input).convert("RGB")
    image_2 = np.array(to_tensor(image_upload_2))

    prediction = model_v4([image.to(device)])

    os.makedirs(output_directory, exist_ok=True)

    get_masks(image_2, prediction, output_directory)


get_segm('./ft61n4fdp5945usv33q0mwzngw19j9j8.jpg', './masks')
