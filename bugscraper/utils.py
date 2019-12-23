#!/usr/bin/env python3
import json
import pandas as pd
from pathlib import Path


def divide_chunks(l, n):

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_dataframe(save_path: Path):
    years = set()

    # Reading the metadata file to get years
    with open(Path(save_path, 'bug_metadata.jsonl')) as mf:
        for line in mf:
            years.add(json.loads(line)['year'])

    dflist = []
    for year in years:
        with open(Path(save_path, str(year) + '.jsonl')) as bf:
            metalist = [json.loads(line) for line in bf]
            dflist.append(pd.DataFrame(metalist))
    df = pd.concat(dflist)
    return df
