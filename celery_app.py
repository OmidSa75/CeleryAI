import celery
import redis
import torch
import torchvision
from torchvision.models.detection import MaskRCNN
from torchvision.models.detection.anchor_utils import AnchorGenerator

device = torch.device('cpu')


def load_model(_self):

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

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)


def inference_model(_self):
    if not hasattr(_self, 'ai_model'):
        _self.ai_model = _self.load_model()
        print('Load AI model')

    input_x = [torch.rand(3, 300, 400).to(
        device), torch.rand(3, 500, 400).to(device)]
    prediction = _self.ai_model(input_x)
    print('Hi, this is a inference function')
    return str(type(prediction))

if __name__ == "__main__":
    celery_app = celery.Celery(
        'main_celery',
        backend='redis://:Eyval@localhost:6379/1',
        broker='redis://:Eyval@localhost:6379/1',
        task_default_queue='AIWithCelery',
    )

    # input_x = [torch.rand(3, 300, 400).to(
    #     device), torch.rand(3, 500, 400).to(device)]
    # prediction = model(input_x)

    celery_app.task(name='inference_model', bind=True,
                    load_model=load_model)(inference_model)
    celery_app.start(['worker', '-l', 'INFO'])
