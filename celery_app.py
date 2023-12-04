import os

import celery
from celery import signals
import torch
import torchvision
from torchvision.models.detection import MaskRCNN
from torchvision.models.detection.anchor_utils import AnchorGenerator

device = torch.device('cuda')
print(f"Device {device} is chosen")


def load_model():

    backbone = torchvision.models.mobilenet_v2().features
    backbone.out_channels = 1280
    anchor_generator = AnchorGenerator(
        sizes=((32, 642, 128, 256, 512,), ),
        aspect_ratios=((0.5, 1.0, 2.0), ),
    )
    roi_pooler = torchvision.ops.MultiScaleRoIAlign(
        featmap_names=['0'],
        output_size=7,
        sampling_ratio=2
    )

    mask_roi_pooler = torchvision.ops.MultiScaleRoIAlign(
        featmap_names=['0'],
        output_size=14,
        sampling_ratio=2,
    )

    model = MaskRCNN(
        backbone,
        num_classes=2,
        rpn_anchor_generator=anchor_generator,
        box_roi_pool=roi_pooler,
        mask_roi_pool=mask_roi_pooler,
    )
    model.eval()
    model.to(device)
    return model


class BaseTask(celery.Task):
    def __init__(self) -> None:
        super().__init__()
        self._ai_model = None
        # signals.worker_init.connect(self.on_worker_init)

    def on_worker_init(self, *args, **kwargs):
        print("Loading AI Model ...")
        self._ai_model = load_model()
        print("AI Model Loaded")

    @property
    def ai_model(self):
        if self._ai_model is None:
            self._ai_model = load_model()
        return self._ai_model


@celery.shared_task(name='inference_model', bind=True, base=BaseTask)
def inference_model(self):
    input_x = [torch.rand(3, 300, 400).to(
        device), torch.rand(3, 500, 400).to(device)]
    prediction = self.ai_model(input_x)
    print('Hi, this is a inference function')
    return str(type(prediction))


if __name__ == "__main__":
    # this forces the application to use spawn instead of fork
    os.environ["FORKED_BY_MULTIPROCESSING"] = "1"
    if os.name != "nt":
        from billiard import context
        context._force_start_method("spawn")
        print('Context is changed to SPAWN')

    celery_app = celery.Celery(
        'main_celery',
        backend='redis://:Eyval@localhost:6379/1',
        broker='redis://:Eyval@localhost:6379/1',
        task_default_queue='AIWithCelery',
        include=['celery_app']
    )

    # celery_app.task(name='inference_model', bind=True,
                    # base=BaseTask)(inference_model)
    celery_app.start(['worker', '-l', 'INFO', '--concurrency', '2'])
