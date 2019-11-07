# -*- coding: utf-8 -*-
import os
import json
import requests
import logging
from typing import Iterable


logger = logging.getLogger('bugscraper')


class BugzillaBugApi(object):
    """
    Simple API class interface to fetch bugs and comments
    """
    def __init__(self, sub_domain: str):
        self.sub_domain = sub_domain

    def bug_url(self, bug_id):
        return str(self) + '/' + str(bug_id)

    def comment_url(self, bug_id):
        return str(self.bug_url(bug_id)) + '/comment'

    def get_bug(self, bug_id):
        try:
            response = requests.get(url=self.bug_url(bug_id))
            response.raise_for_status()
            bug_dict = response.json()['bugs'][0]
        except requests.exceptions.RequestException as e:
            logger.warn('Connection Error: returning None')
            logger.debug(str(e))
            bug_dict = None
        except KeyError as e:
            logger.warn('incorrect key bugs: returning None')
            logger.debug(str(e))
            bug_dict = None
        finally:
            return bug_dict

    def get_comment(self, bug_id):
        try:
            response = requests.get(url=self.comment_url(bug_id))
            response.raise_for_status()
            bug_dict = response.json()['bugs'][str(bug_id)]['comments']
        except requests.exceptions.RequestException as e:
            logger.warning(f'Connection Error: returning None for bug_id: {bug_id}')
            logger.debug(str(e))
            bug_dict = None
        except KeyError as e:
            logger.warning(f'KeyError while fetching comments: returning None for bug_id: {bug_id}')
            logger.debug(str(e))
            bug_dict = None
        finally:
            return bug_dict

    def __str__(self):
        return f'http://bugzilla.{self.sub_domain}.org/rest/bug'


class BugSaver(object):
    """
    Bug Saver utility that saves bug by years in json lines format
    """
    def __init__(self, save_dir, years: Iterable[int]):
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir
        self.bug_fileobjs = {}
        logger.info(f'Opening {len(years)} files for saving bugs')
        for year in years:
            filepath = os.path.join(self.save_dir, str(year) + '.jsonl')
            self.bug_fileobjs[year] = open(filepath, 'a')

    def __enter__(self):
        return self

    def save(self, bug):
        creation_year = int(bug['creation_time'].split('-')[0])
        self.bug_fileobjs[creation_year].write(json.dumps(bug) + '\n')

    def __exit__(self):
        for fileobj in self.bug_fileobjs:
            fileobj.close()
