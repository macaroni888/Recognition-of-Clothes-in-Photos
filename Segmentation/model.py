from torchvision.models.detection import MaskRCNN_ResNet50_FPN_Weights as start_weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
import torchvision


def get_model_v4(num_classes):
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights=start_weights.DEFAULT, box_detections_per_img=20)

    for name, param in model.backbone.named_parameters():
        if 'layer1' in name or 'layer2' in name:
            param.requires_grad = False

    in_features = model.roi_heads.box_predictor.cls_score.in_features

    model.roi_heads.box_roi_pool = torchvision.ops.MultiScaleRoIAlign(
        featmap_names=['0', '1', '2', '3'],
        output_size=7,
        sampling_ratio=2
    )

    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 512

    model.roi_heads.mask_roi_pool = torchvision.ops.MultiScaleRoIAlign(
        featmap_names=['0', '1', '2', '3'],
        output_size=14,
        sampling_ratio=2
    )

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )

    model.roi_heads.mask_iou_thresh = 0.7
    model.roi_heads.score_thresh = 0.05

    return model
