#!/usr/bin/env python3
import json
from pathlib import Path


def divide_chunks(l, n):

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def mozilla_filter(save_path: Path):
    years = set()

    products = ['Core', 'Firefox']

    # Reading the metadata file to get years
    with open(Path(save_path, 'bug_metadata.jsonl')) as mf:
        for line in mf:
            meta = json.loads(line)
            years.add(meta['year'])

    for year in years:
        with open(Path(save_path, str(year) + '.jsonl')) as bf:
            for bugrec in bf:
                bug = json.loads(bf)
                if bug['product'] in products:
                    yield bug
