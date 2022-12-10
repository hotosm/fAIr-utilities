# fairlib ( Utilities for AI Assisted Mapping fAIr )
Initially lib was developed during Open AI Challenge with [Omdeena](https://omdena.com/). Learn more about challenge from [here](https://www.hotosm.org/tech-blog/hot-tech-talk-open-ai-challenge/)  

## `fairlib` Installation

1. Set up a Conda virtual environment for installing `fairlib` using `environment.yml`:

    ```console
    conda env create -f environment.yml
    ```

2. Activate the virtual environment.

    ```console
    conda activate fAIr
    ```

3. Install `fairlib` from PyPI:

    ```console
    pip install fairlib
    ```

## Making Edits to Preprocessing/Inference

Edit in `fairlib`. In order to test your edit, take the following steps:

1. Install `fairlib` package in editable mode:

    ```console
    python -m pip install -e fairlib
    ```

2. Test it by running:

    ```console
    pip list | grep fairlib
    ```


3. Make an edit to `fairlib`.
4. Try running `task_1_preprocessing/preprocess.py` now. The updated code will be executed.

## Custom Virtual Environment

```console
conda create -n fAIr python=3.8
conda activate fAIr
conda install -c conda-forge gdal
conda install -c conda-forge geopandas
pip install pyogrio rasterio tensorflow
pip install -e fairlib
```

## Sort Imports

```console
isort . --profile black -s env
```
