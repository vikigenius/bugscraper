#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `bugscraper` package."""

import pytest
import json
from click.testing import CliRunner

from bugscraper.bugscraper import BugzillaBugApi, BugSaver
from bugscraper import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


@pytest.fixture(scope="module", params=[1, 100])
def kernel_bug(request):
    api = BugzillaBugApi('kernel')
    bug = api.get_bug_with_comments(request.param)
    return bug


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'scrape' in help_result.output


def test_comments(kernel_bug):
    bug = kernel_bug
    assert isinstance(bug, dict)
    assert 'comments' in bug


def test_bug_saver(tmp_path):
    save_dir = tmp_path/'bugs'
    sim_bug = {'creation_time': '2002-11-14T04:48:24Z'}
    saver = BugSaver(save_dir)
    saver.save(sim_bug)
    test_bug_file = save_dir/'2002.jsonl'

    assert test_bug_file.exists()
    assert json.loads(test_bug_file.read_text()) == sim_bug
