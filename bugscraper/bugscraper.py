# -*- coding: utf-8 -*-
import os
import json
import requests
import logging


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

    def get_bug_with_comments(self, bug_id):
        bug_dict = self.get_bug(bug_id)
        comment_dict = self.get_comment(bug_id)
        bug_dict['comments'] = comment_dict
        return bug_dict

    def __str__(self):
        return f'http://bugzilla.{self.sub_domain}.org/rest/bug'


class BugSaver(object):
    """
    Bug Saver utility that saves bug by years in json lines format
    """
    def __init__(self, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir

    def save(self, bug):
        creation_year = bug['creation_time'].split('-')[0]
        filename = creation_year + '.jsonl'
        save_path = os.path.join(self.save_dir, filename)
        with open(save_path, 'a') as bdfile:
            bdfile.write(json.dumps(bug) + '\n')
