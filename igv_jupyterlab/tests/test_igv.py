#!/usr/bin/env python
# coding: utf-8

# Copyright (c) {{ cookiecutter.author_name }}.
# Distributed under the terms of the Modified BSD License.

import pytest

from igv_jupyterlab.igv_widget import IGV


class TestIGV:

    def test_filter_none_removes_nested_keys_with_values_equal_to_none(self):
        data = {
            'test_flat': None,
            'test_nested': {
                'test_nested_1': None
            }
        }

        filtered = IGV._filter_none(data)
        
        with pytest.raises(KeyError):
            filtered['test_flat']

        with pytest.raises(KeyError):
            filtered['test_nested']['test_nested_1']

    def test_init_adds_correct_key_to_initial_config_when_genome_param_is_str(self):
        igv = IGV('hg19')

        assert igv.initialConfig['genome']

        with pytest.raises(KeyError):
            igv.initialConfig['reference']

    def test_init_adds_correct_key_to_initial_config_when_genome_param_is_config(self):
        genome = IGV.create_genome(
            name="Human (GRCh38/hg38)",
            fasta_url="",
        )

        igv = IGV(genome=genome)

        assert igv.initialConfig['reference']

        with pytest.raises(KeyError):
            igv.initialConfig['genome']