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

You can run `package_test.ipynb` to your pc to test the installation and workflow with sample data provided
