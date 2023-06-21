# hot_fair_utilities ( Utilities for AI Assisted Mapping fAIr )

Initially lib was developed during Open AI Challenge with [Omdeena](https://omdena.com/). Learn more about challenge from [here](https://www.hotosm.org/tech-blog/hot-tech-talk-open-ai-challenge/)

## `hot_fair_utilities` Installation

Installing all libraries could be pain so we suggest you to use docker , If you like to do it bare , You can follow `.github/build.yml`

Clone repo

```
git clone https://github.com/hotosm/fAIr-utilities.git
```

Build Docker

```
docker build --tag fairutils .
```

Run Container with default Jupyter Notebook , Or add `bash` at end to see terminal

```
docker run -it --rm --gpus=all  -p 8888:8888 fairutils
```

By Default tf is set as Ramp_Home , You can change that attaching your volume to container as tf

```
-v /home/hotosm/fAIr-utilities:/tf
```

## Test Installation and workflow

You can run `package_test.ipynb` on your notebook from docker to test the installation and workflow with sample data provided , Or open with [collab and connect your runtime locally](https://research.google.com/colaboratory/local-runtimes.html#:~:text=In%20Colab%2C%20click%20the%20%22Connect,connected%20to%20your%20local%20runtime.)
