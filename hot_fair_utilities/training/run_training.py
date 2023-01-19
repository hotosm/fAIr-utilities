# Standard library imports
import os

# Third party imports
import tensorflow as tf

# Assert that the version of the library is greater than or equal to 2.9.2
assert tf.__version__ <= "2.9.2"  # tested up to 2.9.2

# Standard library imports

# Standard library imports
import datetime
import json
import os
from pathlib import Path
from time import perf_counter

# Third party imports
import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow import keras

# Note: this suppresses warning and other less urgent messages,
# and only allows errors to be printed.
# Comment this out if you are having mysterious problems, so you can see all messages.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


class RaiseError(Exception):
    def __init__(self, message):
        self.message = message


# Third party imports

# Third party imports
import segmentation_models as sm
from ramp.data_mgmt.data_generator import (
    test_batches_from_gtiff_dirs,
    training_batches_from_gtiff_dirs,
)
from ramp.training import (
    callback_constructors,
    loss_constructors,
    metric_constructors,
    model_constructors,
    optimizer_constructors,
)

# import ramp dependencies.
from ramp.training.augmentation_constructors import get_augmentation_fn
from ramp.utils.misc_ramp_utils import get_num_files

# Segmentation Models: using `keras` framework.
sm.set_framework("tf.keras")


# this variable must be defined. It is the parent of the 'ramp-code' directory.
working_ramp_home = os.environ["RAMP_HOME"]


def manage_fine_tuning_config(output_path, num_epochs, batch_size):

    # Define the paths to the source and destination JSON files
    working_dir = os.path.realpath(os.path.dirname(__file__))
    config_base_path = os.path.join(working_dir, "data/ramp_config_base.json")
    dst_path = os.path.join(output_path, "ramp_fair_config_finetune.json")

    # Read the content of the source JSON file
    with open(config_base_path, "r") as f:
        data = json.load(f)

    # Modify the content of the data dictionary datasets
    data["datasets"]["train_img_dir"] = f"{output_path}/chips"
    data["datasets"]["train_mask_dir"] = f"{output_path}/binarymasks"
    data["datasets"]["val_img_dir"] = f"{output_path}/val-chips"
    data["datasets"]["val_mask_dir"] = f"{output_path}/val-binarymasks"

    # epoch batchconfig
    data["num_epochs"] = num_epochs
    data["batch_size"] = batch_size

    # clr plot
    data["cyclic_learning_scheduler"]["clr_plot_dir"] = f"{output_path}/plots"
    # logs
    data["tensorboard"]["tb_logs_dir"] = f"{output_path}/logs"
    # output images
    data["graph_location"] = f"{output_path}/graphs"
    # model_checkpts
    data["model_checkpts"]["model_checkpts_dir"] = f"{output_path}/model-checkpts"
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

    # Construct the loss function
    loss_fn = get_loss_fn(cfg)

    the_metrics = []
    if cfg["metrics"]["use_metrics"]:

        get_metrics_fn_names = cfg["metrics"]["get_metrics_fn_names"]
        get_metrics_fn_parms = cfg["metrics"]["metrics_fn_parms"]

        for get_mf_name, mf_parms in zip(get_metrics_fn_names, get_metrics_fn_parms):
            get_metric_fn = getattr(metric_constructors, get_mf_name)
            print(f"Metric constructor function: {get_metric_fn.__name__}")
            metric_fn = get_metric_fn(mf_parms)
            the_metrics.append(metric_fn)

    #### construct optimizer ####

    get_optimizer_fn_name = cfg["optimizer"]["get_optimizer_fn_name"]
    get_optimizer_fn = getattr(optimizer_constructors, get_optimizer_fn_name)

    optimizer = get_optimizer_fn(cfg)

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

        # get tensorboard callback
        if cfg["tensorboard"]["use_tb"]:
            get_tb_callback_fn_name = cfg["tensorboard"]["get_tb_callback_fn_name"]
            get_tb_callback_fn = getattr(callback_constructors, get_tb_callback_fn_name)
            callbacks_list.append(get_tb_callback_fn(cfg))

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

    # free up RAM
    keras.backend.clear_session()

    if cfg["early_stopping"]["use_early_stopping"]:

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

    ## Main training block ##
    n_epochs = cfg["num_epochs"]
    print(
        f"Starting Training with {n_epochs} epochs , {batch_size} batch size , {steps_per_epoch} steps per epoch , {validation_steps} validation steps......"
    )
    if validation_steps <= 0:
        raise RaiseError("Not enough data for training")
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
    print(f"Training Finished , Time taken to train : {end-start} seconds")

    # plot the training and validation accuracy and loss at each epoch
    print("Generating graphs ....")
    if not os.path.exists(cfg["graph_location"]):
        os.mkdir(cfg["graph_location"])

    loss = history.history["loss"]
    # val_loss = history.history["val_loss"]
    epochs = range(1, len(loss) + 1)

    # plt.plot(epochs, loss, "y", label="Training loss")
    # plt.plot(epochs, val_loss, "r", label="Validation loss")
    # plt.title("Training and validation loss")
    # plt.xlabel("Epochs")
    # plt.ylabel("Loss")
    # plt.legend()
    # plt.savefig(f"{cfg['graph_location']}/training_validation_loss.png")

    acc = history.history["sparse_categorical_accuracy"]
    val_acc = history.history["val_sparse_categorical_accuracy"]
    plt.plot(epochs, acc, "y", label="Training acc")
    plt.plot(epochs, val_acc, "r", label="Validation sparse categorical acc")
    plt.title("Training and validation sparse categorical accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Sparse Categorical Accuracy")
    plt.legend()
    plt.savefig(
        f"{cfg['graph_location']}/training_validation_sparse_categorical_accuracy.png"
    )
    print(f"Graph generated at : {cfg['graph_location']}")
