# -*- coding: utf-8 -*-
import os
import re
import json
import requests
import logging
from typing import Iterable, List, Any
from dataclasses import dataclass, field, asdict
from pathlib import PurePath


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


class BugzillaCommentApi(object):
    """
    Simple API class interface to fetch bugs
    """
    def __init__(self, sub_domain: str):
        self.sub_domain = sub_domain

    def fetch(self, bug_id: int):
        try:
            response = requests.get(url=str(self) + f'/{bug_id}/comment')
            response.raise_for_status()
            comment_list = response.json()['bugs'][str(bug_id)]['comments']
        except requests.exceptions.RequestException as e:
            logger.warn('Connection Error: returning None')
            logger.debug(str(e))
            comment_list = []
        except KeyError as e:
            logger.warn('incorrect key: returning None')
            logger.debug(str(e))
            comment_list = []
        finally:
            return comment_list

    def __str__(self):
        return f'http://bugzilla.{self.sub_domain}.org/rest/bug'


@dataclass
class BugSaveMetadata:
    bug_id: str = ''
    year: int = -1
    comment_ids: List[str] = field(default_factory=list)

    @classmethod
    def from_json(cls: 'BugSaveMetadata', json_str: str):
        bug_dict = json.loads(json_str)
        return cls(str(bug_dict['bug_id']), bug_dict['year'], bug_dict['comment_ids'])


class Saver(object):
    def __init__(self, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir
        self.bug_metadata: List[BugSaveMetadata] = []
        self.fileobjs = {}

    def load_metadata(self):
        metadata_path = PurePath(self.save_dir, 'bug_metatada.jsonl')
        with open(metadata_path) as mf:
            for line in mf:
                self.bug_metadata.append(BugSaveMetadata.from_json(line))
        logger.info('Loaded Metadata')
        return self.bug_metadata

    def save_metadata(self):
        metadata_path = PurePath(self.save_dir, 'bug_metatada.jsonl')
        with open(metadata_path, 'w') as mf:
            for meta in self.bug_metadata:
                mf.write(json.dumps(asdict(meta)) + '\n')

        logger.info('Saved Metadata to file: {}'.format(metadata_path))

    def __del__(self):
        for _, fileobj in self.fileobjs.items():
            fileobj.close()


class BugSaver(Saver):
    """
    Bug Saver utility that saves bug by years in json lines format
    "TODO: Allow more granularity in file access"
    """
    def __init__(self, save_dir, years: Iterable[int], num_chunks: int):
        super().__init__(save_dir)

        # Check if metadata exists
        try:
            self.load_metadata()
        except Exception as e:
            logger.debug('Metadata does not exist: {}'.format(e))

        logger.info(f'Opening {len(years)} files for saving bugs')
        for year in years:
            filepath = os.path.join(self.save_dir, str(year) + '.jsonl')
            self.fileobjs[year] = open(filepath, 'a')

    def save(self, bug_list: Iterable[int]):
        for bug in bug_list:
            creation_year = int(bug['creation_time'].split('-')[0])
            self.fileobjs[creation_year].write(json.dumps(bug) + '\n')
            self.bug_metadata.append(BugSaveMetadata(str(bug['id']), creation_year, []))


# Regex to capture year name in file
file_regex = re.compile(r'^((?:19|20)\d{2}).jsonl$')


class CommentSaver(Saver):
    """
    Comment Saver utility that saves bug by years in json lines format
    "TODO: Allow more granularity in file access"
    """
    def __init__(self, save_dir):
        super().__init__(save_dir)

        # Check if metadata exists
        try:
            self.load_metadata()
        except Exception as e:
            logger.debug('Metadata does not exist: {}'.format(e))
            logger.debug('Loading Metadata from bug files')
            self.collect_bug_metadata()

        years = [metadata.year for metadata in self.bug_metadata]
        years = list(set(years))
        logger.info(f'Opening {len(years)} files for saving comments')
        for year in years:
            filepath = os.path.join(self.save_dir, str(year) + '_comments.jsonl')
            self.fileobjs[year] = open(filepath, 'a')

    def save(self, meta_idx: int, comments: List[Any]):
        bug = self.bug_metadata[meta_idx]
        cdict = {bug.bug_id: comments}
        self.fileobjs[bug.year].write(json.dumps(cdict) + '\n')
        comment_ids = [str(comment['id']) for comment in comments]
        self.bug_metadata[meta_idx].comment_ids = comment_ids

    # Returns the bug metadata post simple checks
    def collect_bug_metadata(self):
        for path, directories, files in os.walk(self.save_dir):
            for filename in files:
                match = file_regex.match(filename)
                if match:
                    year = int(match.group(1))
                    # Now open the file for reading

                    filepath = os.path.join(self.save_dir, filename)
                    with open(filepath) as bf:
                        for line in bf:
                            bug = json.loads(line)
                            self.bug_metadata.append(BugSaveMetadata(str(bug['id']), year, []))
        return self.bug_metadata
