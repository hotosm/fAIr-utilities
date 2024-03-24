import torch
import torch.nn as nn
import ultralytics

from ultralytics.utils import RANK


#
# Binary cross entropy with p_c
#

class YOLOSegWithPosWeight(ultralytics.YOLO):

    def train(self, trainer=None, pc=1.0, **kwargs):
        return super().train(trainer, **{**kwargs, "pose": pc})  # Hide pc inside pose (pose est loss weight arg)

    @property
    def task_map(self):
        map = super().task_map
        map['segment']['model'] = SegmentationModelWithPosWeight
        map['segment']['trainer'] = SegmentationTrainerWithPosWeight
        return map


class SegmentationTrainerWithPosWeight(ultralytics.models.yolo.segment.train.SegmentationTrainer):

    def get_model(self, cfg=None, weights=None, verbose=True):
        """Return a YOLO segmentation model."""
        model = SegmentationModelWithPosWeight(cfg, nc=self.data['nc'], verbose=verbose and RANK == -1)
        if weights:
            model.load(weights)
        return model


class SegmentationModelWithPosWeight(ultralytics.models.yolo.segment.train.SegmentationModel):

    def init_criterion(self):
        return v8SegmentationLossWithPosWeight(model=self)


class v8SegmentationLossWithPosWeight(ultralytics.utils.loss.v8SegmentationLoss):

    def __init__(self, model):
        super().__init__(model)
        pc = model.args.pose  # hidden in pose arg (used in different task)
        pos_weight = torch.full((model.nc,), pc).to(self.device)
        self.bce = nn.BCEWithLogitsLoss(reduction="none", pos_weight=pos_weight)
