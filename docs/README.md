# Documentation of fAIr-lib-python with Sphinx

[Sphinx](https://www.sphinx-doc.org/) is a python library for generating documentation based on docstrings.

## Installation of Sphinx into the conda environment 'hot'

```console
   activate hot
   conda install sphinx
   pip install sphinx_rtd_theme
```

## Generation of HTML documentation for the fAIr-lib-python library

```console
   cd fAIr-lib-python/docs
   sphinx-build -b html source build
```

## Generation of LaTeX/PDF documentation for the fAIr-lib-python library

```console
   cd fAIr-lib-python/docs
   sphinx-build -M latexpdf source build
```
