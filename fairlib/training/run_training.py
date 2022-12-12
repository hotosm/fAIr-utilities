# Standard library imports
import os

# Third party imports
import tensorflow as tf

# Assert that the version of the library is greater than or equal to 2.9.2
assert tf.__version__ <= "2.9.2"  # tested up to 2.9.2

# Standard library imports
import argparse
import datetime
import json
import os
import random
import sys
from pathlib import Path
from time import perf_counter

# Third party imports
import keras.backend as K
import numpy as np
import tensorflow as tf
from tensorflow import keras

# Note: this suppresses warning and other less urgent messages,
# and only allows errors to be printed.
# Comment this out if you are having mysterious problems, so you can see all messages.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


# Third party imports
import ramp.utils.log_fields as lf
import segmentation_models as sm
from ramp.data_mgmt.data_generator import (
    test_batches_from_gtiff_dirs,
    training_batches_from_gtiff_dirs,
)
from ramp.models.effunet_1 import get_effunet
from ramp.training import (
    callback_constructors,
    loss_constructors,
    metric_constructors,
    model_constructors,
    optimizer_constructors,
)

# import ramp dependencies.
from ramp.training.augmentation_constructors import get_augmentation_fn
from ramp.utils.misc_ramp_utils import get_num_files, log_experiment_to_file
from ramp.utils.model_utils import get_best_model_value_and_epoch

# Segmentation Models: using `keras` framework.
sm.set_framework("tf.keras")


# this variable must be defined. It is the parent of the 'ramp-code' directory.
working_ramp_home = os.environ["RAMP_HOME"]
print(working_ramp_home)


def manage_fine_tuning_config(uid, num_epochs, batch_size):

    # Define the paths to the source and destination JSON files
    working_dir = os.path.realpath(os.path.dirname(__file__))
    config_base_path = os.path.join(working_dir, "data/ramp_config_base.json")
    dst_path = (
        Path(working_ramp_home) / f"ramp-code/data/ramp_fair_config_finetune_{uid}.json"
    )

    # Read the content of the source JSON file
    with open(config_base_path, "r") as f:
        data = json.load(f)

    # Modify the content of the data dictionary datasets
    data["datasets"]["train_img_dir"] = f"ramp-data/TRAIN/{uid}/chips"
    data["datasets"]["train_mask_dir"] = f"ramp-data/TRAIN/{uid}/binarymasks"
    data["datasets"]["val_img_dir"] = f"ramp-data/TRAIN/{uid}/val-chips"
    data["datasets"]["val_mask_dir"] = f"ramp-data/TRAIN/{uid}/val-binarymasks"

    # epoch batchconfig
    data["num_epochs"] = num_epochs
    data["batch_size"] = batch_size

    # clr plot
    data["cyclic_learning_scheduler"]["clr_plot_dir"] = f"ramp-data/TRAIN/{uid}/plots"
    # logs
    data["tensorboard"]["tb_logs_dir"] = f"ramp-data/TRAIN/{uid}/logs"
    # model_checkpts
    data["model_checkpts"][
        "model_checkpts_dir"
    ] = f"ramp-data/TRAIN/{uid}/model-checkpts"
    # save best models only
    data["model_checkpts"]["model_checkpt_callback_parms"]["save_best_only"] = True
    # Open the destination file and write the modified data
    with open(dst_path, "w") as f:
        json.dump(data, f)

    return data


def run_main_train_code(cfg):
    discard_experiment = False
    if "discard_experiment" in cfg:
        discard_experiment = cfg["discard_experiment"]

    cfg["timestamp"] = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # specify a function that will construct the loss function
    get_loss_fn_name = cfg["loss"]["get_loss_fn_name"]
    get_loss_fn = getattr(loss_constructors, get_loss_fn_name)
    print(f"Loss function constructor: {get_loss_fn.__name__}")

    # Construct the loss function
    loss_fn = get_loss_fn(cfg)
    print(f"Loss function: {loss_fn.__name__}")

    the_metrics = []
    if cfg["metrics"]["use_metrics"]:

        get_metrics_fn_names = cfg["metrics"]["get_metrics_fn_names"]
        get_metrics_fn_parms = cfg["metrics"]["metrics_fn_parms"]

        for get_mf_name, mf_parms in zip(get_metrics_fn_names, get_metrics_fn_parms):
            get_metric_fn = getattr(metric_constructors, get_mf_name)
            print(f"Metric constructor function: {get_metric_fn.__name__}")
            metric_fn = get_metric_fn(mf_parms)
            the_metrics.append(metric_fn)

    # Print the list of accuracy metrics
    print(f"Accuracy metrics: {[fn.name for fn in the_metrics]}")

    #### construct optimizer ####

    get_optimizer_fn_name = cfg["optimizer"]["get_optimizer_fn_name"]
    get_optimizer_fn = getattr(optimizer_constructors, get_optimizer_fn_name)
    print(f"Optimizer constructor: {get_optimizer_fn.__name__}")

    optimizer = get_optimizer_fn(cfg)
    print(optimizer)
    print(float(optimizer.learning_rate))

    the_model = None

    if cfg["saved_model"]["use_saved_model"]:

        # load (construct) the model
        model_path = Path(working_ramp_home) / cfg["saved_model"]["saved_model_path"]
        print(f"Model: importing saved model {str(model_path)}")
        the_model = tf.keras.models.load_model(model_path)
        assert (
            the_model is not None
        ), f"the saved model was not constructed: {model_path}"

        if not cfg["saved_model"]["save_optimizer_state"]:
            # If you don't want to save the original state of training, recompile the model.
            the_model.compile(optimizer=optimizer, loss=loss_fn, metrics=[the_metrics])

            # the_model.compile(optimizer = optimizer,
            #    loss=loss_fn,
            #    metrics = [get_iou_coef_fn])

    if not cfg["saved_model"]["use_saved_model"]:
        get_model_fn_name = cfg["model"]["get_model_fn_name"]
        get_model_fn = getattr(model_constructors, get_model_fn_name)
        print(f"Model constructor: {get_model_fn.__name__}")
        the_model = get_model_fn(cfg)

        assert the_model is not None, f"the model was not constructed: {model_path}"
        the_model.compile(optimizer=optimizer, loss=loss_fn, metrics=the_metrics)

    print(the_model)
    cfg["datasets"]

    #### define data directories ####
    train_img_dir = Path(working_ramp_home) / cfg["datasets"]["train_img_dir"]
    train_mask_dir = Path(working_ramp_home) / cfg["datasets"]["train_mask_dir"]
    val_img_dir = Path(working_ramp_home) / cfg["datasets"]["val_img_dir"]
    val_mask_dir = Path(working_ramp_home) / cfg["datasets"]["val_mask_dir"]

    #### get the augmentation transform ####
    # aug = None
    if cfg["augmentation"]["use_aug"]:
        aug = get_augmentation_fn(cfg)
        print(aug)

    ## RUNTIME Parameters
    batch_size = cfg["batch_size"]
    input_img_shape = cfg["input_img_shape"]
    output_img_shape = cfg["output_img_shape"]

    n_training = get_num_files(train_img_dir, "*.tif")
    n_val = get_num_files(val_img_dir, "*.tif")
    steps_per_epoch = n_training // batch_size
    validation_steps = n_val // batch_size

    # add these back to the config
    # in case they are needed by callbacks
    cfg["runtime"] = {}
    cfg["runtime"]["n_training"] = n_training
    cfg["runtime"]["n_val"] = n_val
    cfg["runtime"]["steps_per_epoch"] = steps_per_epoch
    cfg["runtime"]["validation_steps"] = validation_steps

    train_batches = None

    if aug is not None:
        train_batches = training_batches_from_gtiff_dirs(
            train_img_dir,
            train_mask_dir,
            batch_size,
            input_img_shape,
            output_img_shape,
            transforms=aug,
        )
    else:
        train_batches = training_batches_from_gtiff_dirs(
            train_img_dir, train_mask_dir, batch_size, input_img_shape, output_img_shape
        )

    assert train_batches is not None, "training batches were not constructed"

    val_batches = test_batches_from_gtiff_dirs(
        val_img_dir, val_mask_dir, batch_size, input_img_shape, output_img_shape
    )

    assert val_batches is not None, "validation batches were not constructed"

    ## Callbacks ##
    callbacks_list = []

    if not discard_experiment:

        # get model checkpoint callback
        if cfg["model_checkpts"]["use_model_checkpts"]:
            get_model_checkpt_callback_fn_name = cfg["model_checkpts"][
                "get_model_checkpt_callback_fn_name"
            ]
            get_model_checkpt_callback_fn = getattr(
                callback_constructors, get_model_checkpt_callback_fn_name
            )
            callbacks_list.append(get_model_checkpt_callback_fn(cfg))
            print(
                f"model checkpoint callback constructor:{get_model_checkpt_callback_fn.__name__}"
            )

        # get tensorboard callback
        if cfg["tensorboard"]["use_tb"]:
            get_tb_callback_fn_name = cfg["tensorboard"]["get_tb_callback_fn_name"]
            get_tb_callback_fn = getattr(callback_constructors, get_tb_callback_fn_name)
            callbacks_list.append(get_tb_callback_fn(cfg))
            print(f"tensorboard callback constructor: {get_tb_callback_fn.__name__}")

        # get tensorboard model prediction logging callback
        if cfg["prediction_logging"]["use_prediction_logging"]:
            assert cfg["tensorboard"][
                "use_tb"
            ], "Tensorboard logging must be turned on to enable prediction logging"
            get_prediction_logging_fn_name = cfg["prediction_logging"][
                "get_prediction_logging_fn_name"
            ]
            get_prediction_logging_fn = getattr(
                callback_constructors, get_prediction_logging_fn_name
            )
            callbacks_list.append(get_prediction_logging_fn(the_model, cfg))
            print(
                f"prediction logging callback constructor: {get_prediction_logging_fn.__name__}"
            )

    # free up RAM
    keras.backend.clear_session()

    if cfg["early_stopping"]["use_early_stopping"]:
        print("Using early stopping")
        callbacks_list.append(callback_constructors.get_early_stopping_callback_fn(cfg))

        # get cyclic learning scheduler callback
    if cfg["cyclic_learning_scheduler"]["use_clr"]:
        assert not cfg["early_stopping"][
            "use_early_stopping"
        ], "cannot use early_stopping with cycling_learning_scheduler"
        get_clr_callback_fn_name = cfg["cyclic_learning_scheduler"][
            "get_clr_callback_fn_name"
        ]
        get_clr_callback_fn = getattr(callback_constructors, get_clr_callback_fn_name)
        callbacks_list.append(get_clr_callback_fn(cfg))
        print(f"CLR callback constructor: {get_clr_callback_fn.__name__}")

    ## Main training block ##
    n_epochs = cfg["num_epochs"]
    print(n_epochs)
    # FIXME : Make checkpoint
    start = perf_counter()
    history = the_model.fit(
        train_batches,
        epochs=n_epochs,
        steps_per_epoch=steps_per_epoch,
        validation_data=val_batches,
        validation_steps=validation_steps,
        callbacks=callbacks_list,
    )
    end = perf_counter()
    print(f"Time taken to train code : {end-start} seconds")
