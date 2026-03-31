import logging
from pathlib import Path

import geopandas as gpd

log = logging.getLogger(__name__)

try:
    from ramp.utils.eval_utils import get_iou_accuracy_metrics
except ImportError:
    log.warning("Ramp eval metrics are not available, possibly ramp is not installed")


def evaluate(test_path, truth_path, filter_area_m2=None, iou_threshold=0.5, verbose=False):
    """
    Calculate precision/recall/F1-score based on intersection-over-union accuracy evaluation protocol defined by RAMP.

    The predicted masks will be georeferenced with EPSG:3857 as CRS
    Args:
        test_path: Path where the weights of the model can be found.
        truth_path: Path of the directory where the images are stored.
        filter_area_m2: Minimum area of buildings to analyze in m^2.
        iou_threshold: (float, 0<threshold<1) above which value of IoU of a detection is considered to be accurate
        verbose: Bool, more statistics are printed when turned on.

    Example::
        evaluate(
            "data/prediction.geojson",
            "data/labels.geojson"
        )
    """

    test_path, truth_path = Path(test_path), Path(truth_path)
    truth_df, test_df = gpd.read_file(str(truth_path)), gpd.read_file(str(test_path))
    metrics = get_iou_accuracy_metrics(test_df, truth_df, filter_area_m2, iou_threshold)

    n_detections = metrics["n_detections"]
    n_truth = metrics["n_truth"]
    n_truepos = metrics["true_pos"]
    n_falsepos = n_detections - n_truepos
    n_falseneg = n_truth - n_truepos
    agg_precision = n_truepos / n_detections
    agg_recall = n_truepos / n_truth
    agg_f1 = 2 * n_truepos / (n_truth + n_detections)

    if verbose:
        log.info("Detections: %d", n_detections)
        log.info("Truth buildings: %d", n_truth)
        log.info("True positives: %d", n_truepos)
        log.info("False positives: %d", n_falsepos)
        log.info("False negatives: %d", n_falseneg)
        log.info("Precision IoU@p: %.4f", agg_precision)
        log.info("Recall IoU@p: %.4f", agg_recall)
        log.info("F1 IoU@p: %.4f", agg_f1)

    return {
        "precision": agg_precision,
        "recall": agg_recall,
        "f1": agg_f1,
    }
