#!/usr/bin/env python
# coding: utf-8

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'nbextension/static',
        'dest': 'igv_jupyterlab',
        'require': 'igv_jupyterlab/extension'
    }]
