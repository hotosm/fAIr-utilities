## v2.0.8 (2025-01-09)

### Fix

- **config**: added ramp config json in setup files
- **workflow**: change installation method to use setup.py in build configuration
- **workflow**: update Python version to 3.9 in build configuration

## v2.0.7 (2025-01-08)

### Fix

- **version**: fixes sub packages not being included in the packaging

## v2.0.6 (2024-11-25)

### Fix

- **version**: loosen version for torch

## v2.0.5 (2024-11-25)

### Fix

- **version**: loosen version of pandas

## v2.0.4 (2024-11-25)

### Fix

- **build**: fixes geopandas

## v2.0.3 (2024-11-25)

### Fix

- **onnx**: supports onnx output of the yolo models for the inference

## v2.0.2 (2024-11-23)

### Fix

- **lib**: remove hard gdal installation requirements

## v2.0.1 (2024-11-22)

### Feat

- **yololib**: adds lib required for packaging yolo code

### Fix

- **dependencies**: downgrade geopandas version to 0.14.4
- **dependencies**: update geopandas version to 1.0.0
- **version-fix**: fixes version of geopandas
- **libversion**: added version of pandas and other integration
- **bundlelib**: bundles lib itself with new pandas version

### Refactor

- **preprocessing**: clean up imports and improve code formatting

## v2.0.0 (2024-11-15)

### Feat

- **yololib**: adds lib required for packaging yolo code
- replace FastSAM with YOLO including training
- add FastSAM inference

### Fix

- **postprocessing/utils**: resolve OAM-x-y-z.mask.tif
- **predict**: support both .png and .tif in inference

## v1.3.0 (2024-10-04)

### Feat

- **multimasks**: binary or multimasks option in training

### Fix

- **multimasks**: fix bug on inconsistency between different zoom levels

### Perf

- **preprocess**: accepts input in meters instead of pixel width for better user understanding

## v1.2.3 (2023-10-26)

### Fix

- version update

## v1.2.2 (2023-08-23)

### Fix

- Made vectorize to accept options in parameters

## v1.2.1 (2023-08-21)

### Fix

- Hotfix

## v1.2.0 (2023-08-14)

### Feat

- Lower Layers Freeze on Feedback

## v1.1.3 (2023-08-14)

### Fix

- Typo fix on manage config

## v1.1.2 (2023-08-03)

### Fix

- Fixed bug on Training Charts Repettion figures

## v1.1.1 (2023-07-24)

### Fix

- Fix on docs

## v1.1.0 (2023-07-24)

### Feat

- version control

## v1.0.52 (2023-06-20)

## v1.0.51 (2023-06-14)
