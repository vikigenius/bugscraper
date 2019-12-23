#!/usr/bin/env python3
import json
import logging
import pandas as pd
from pathlib import Path


logger = logging.getLogger('bugscraper')


def divide_chunks(l, n):

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_dataframe(save_path: Path):
    years = set()

    products = ['Core', 'Firefox', 'Toolkit']

    # Reading the metadata file to get years
    logger.debug('Reading metadata file to get years')
    with open(Path(save_path, 'bug_metadata.jsonl')) as mf:
        for line in mf:
            years.add(json.loads(line)['year'])

    logger.debug(f'Available Years: {years}')
    dflist = []
    for year in years:
        logger.debug(f'Reading Year: {year}')
        with open(Path(save_path, str(year) + '.jsonl')) as bf:
            metalist = [json.loads(line) for line in bf]
            df = pd.DataFrame(metalist)
            df = df[df['product'].isin(products)]
            dflist.append(df)

    logger.debug('Concatenating Dataframes')
    df = pd.concat(dflist)
    return df
