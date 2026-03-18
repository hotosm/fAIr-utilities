from .georeferencing import georeference
from .postprocessing import polygonize, vectorize
from .preprocessing import preprocess, yolo_v8_v1
from .utils import bbox2tiles, tms2img

# TF and torch are optional; only load when predict/evaluate is called.
def predict(*args, **kwargs):
    """Lazy entry-point. Imports TF (RAMP) or PyTorch (YOLO) only when called.
    pip install .[ramp] or .[yolo]
    """
    from .inference.predict import predict as _predict
    return _predict(*args, **kwargs)


def evaluate(*args, **kwargs):
    """Lazy entry-point. Imports ramp.utils.eval_utils only when called.
    pip install .[ramp]
    """
    from .inference.evaluate import evaluate as _evaluate
    return _evaluate(*args, **kwargs)

