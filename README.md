# fairlib ( Utilities for AI Assisted Mapping fAIr )
Initially lib was developed during Open AI Challenge with [Omdeena](https://omdena.com/). Learn more about challenge from [here](https://www.hotosm.org/tech-blog/hot-tech-talk-open-ai-challenge/)  

## `fairlib` Installation

fairlib is collection of utilities which contains core logic for model data prepration , training and postprocessing . It can support multiple models , Currently ramp is supported. 


1. Install tensorflow ```2.9.2``` from [here] (https://www.tensorflow.org/install/pip) According to your os

### Setup Ramp : 

2. Clone ramp working dir 

    ```
    git clone https://github.com/kshitijrajsharma/ramp-code-fAIr.git ramp-code
    ```

3. Install native bindings 
    - Install [gdal](https://gdal.org/index.html) .

        for eg : on Ubuntu 
        ```
        sudo apt-get update && sudo apt-get -y install gdal-bin python3-gdal && sudo apt-get -y autoremove && sudo apt-get clean
        ```
        on conda : 
        ```
        conda install -c conda-forge gdal
        ```
    - Install rasterio 

        for eg: on ubuntu : 
        ```
        sudo apt-get install -y python3-rasterio
        ```
        on conda : 
        ```
        conda install -c conda-forge rasterio
        ```

3. Install ramp requirements 

    Install necessary requirements for ramp 
        ```
        cd colab && make install 
        ```

4. Install fairlib 

        ```
        pip intall fairlib==1.0.35
        ```


## Custom Virtual Environment

    ```
    conda create -n fAIr python=3.8
    conda activate fAIr
    conda install -c conda-forge gdal
    conda install -c conda-forge geopandas
    pip install pyogrio rasterio tensorflow
    pip install -e fairlib
    ```

## Test Installation and workflow 

You can run ```package_test.ipynb``` to your pc to test the installation and workflow with sample data provided 
