# -*- coding: utf-8 -*-
import os
import json
import requests
import logging
from typing import Iterable, List


logger = logging.getLogger('bugscraper')


class BugzillaBugApi(object):
    """
    Simple API class interface to fetch bugs
    """
    def __init__(self, sub_domain: str):
        self.sub_domain = sub_domain

    def fetch(self, bug_ids: Iterable[int]) -> List[int]:
        try:
            response = requests.get(url=str(self), params={'id': list(bug_ids)})
            response.raise_for_status()
            bug_list = response.json()['bugs']
        except requests.exceptions.RequestException as e:
            logger.warn('Connection Error: returning None')
            logger.debug(str(e))
            bug_list = []
        except KeyError as e:
            logger.warn('incorrect key bugs: returning None')
            logger.debug(str(e))
            bug_list = []
        finally:
            return bug_list

    def __str__(self):
        return f'http://bugzilla.{self.sub_domain}.org/rest/bug?'


class BugSaver(object):
    """
    Bug Saver utility that saves bug by years in json lines format
    "TODO: Allow more granularity in file access"
    """
    def __init__(self, save_dir, years: Iterable[int], num_chunks: int):
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir
        self.bug_metadata = []
        self.bug_fileobjs = {}
        self.metadata_path = os.path.join(self.save_dir, 'bug_meta.txt')

        # Check if metadata exists
        try:
            with open(self.metadata_path) as mf:
                for line in mf:
                    self.bug_metadata.append(int(line))
            logger.info('Loaded Metadata')
        except Exception as e:
            logger.debug('Metadata does not exist: {}'.format(e))

        logger.info(f'Opening {len(years)} files for saving bugs')
        for year in years:
            filepath = os.path.join(self.save_dir, str(year) + '.jsonl')
            self.bug_fileobjs[year] = open(filepath, 'a')

    def save(self, bug_list: Iterable[int]):
        for bug in bug_list:
            creation_year = int(bug['creation_time'].split('-')[0])
            self.bug_fileobjs[creation_year].write(json.dumps(bug) + '\n')
            self.bug_metadata.append(bug['id'])

    def save_metadata(self):
        with open(self.metadata_path, 'w') as mp:
            for meta in self.bug_metadata:
                mp.write(meta + '\n')
            logger.info('Saved Metadata to file: {}'.format(self.metadata_path))

    def __del__(self):
        for _, fileobj in self.bug_fileobjs.items():
            fileobj.close()
