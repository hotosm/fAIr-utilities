# hot_fair_utilities ( Utilities for AI Assisted Mapping fAIr )

Initially lib was developed during Open AI Challenge with [Omdeena](https://omdena.com/). Learn more about challenge from [here](https://www.hotosm.org/tech-blog/hot-tech-talk-open-ai-challenge/)


## Prerequisties

- Install gdal-python and numpy array

## `hot_fair_utilities` Installation

Installing all libraries could be pain so we suggest you to use docker , If you like to do it bare , You can follow `.github/build.yml`

<!-- comment -->

Clone repo

```
git clone https://github.com/hotosm/fAIr-utilities.git
```

Navigate to fAIr-utilities

```
cd fAIr-utilities
```
Build Docker

```
docker build --tag fairutils .
```

Run Container with default Jupyter Notebook , Or add `bash` at end to see terminal

```
docker run -it --rm --gpus=all  -p 8888:8888 fairutils
```

[Optional] If you have downloaded RAMP already , By Default tf is set as Ramp_Home , You can change that by attaching your ramp-home volume to container as tf

if not you can skip this step , Ramp code will be downloaded on package_test.ipynb

```
-v /home/hotosm/fAIr-utilities:/tf
```

## Test inside Docker Container

```
docker run -it --rm --gpus=all  -p 8888:8888 fairutils bash
```

```
python test_app.py
```

## Test Installation and workflow

You can run [`package_test.ipynb`](./Package_Test.ipynb) on your notebook from docker to test the installation and workflow with sample data provided , Or open with [collab and connect your runtime locally](https://research.google.com/colaboratory/local-runtimes.html#:~:text=In%20Colab%2C%20click%20the%20%22Connect,connected%20to%20your%20local%20runtime.)

## Get started with development

Now you can play with your data , use your own data , use different models for testing and also Help me Improve me !

### Version Control
Follow [Version Control Docs](./docs/Version_control.md) to publish and maintain new version

master --- > Dev  
Releases ---- > Production