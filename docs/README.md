# Documentation of hot_fair_utilities with Sphinx

[Sphinx](https://www.sphinx-doc.org/) is a python library for generating documentation based on docstrings.

## Installation of Sphinx into the conda environment 'hot'

```console
   activate hot
   conda install sphinx
   pip install sphinx_rtd_theme
```

## Generation of HTML documentation for the hot_fair_utilities library

```console
   cd hot_fair_utilities/docs
   sphinx-build -b html source build
```

## Generation of LaTeX/PDF documentation for the hot_fair_utilities library

```console
   cd hot_fair_utilities/docs
   sphinx-build -M latexpdf source build
```
