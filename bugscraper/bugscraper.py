# -*- coding: utf-8 -*-
import os
import time
import json
import requests
from dataclasses import dataclass


@dataclass
class BugzillaBugApiUrl:
    sub_domain: str = 'mozilla'

    def __repr__(self):
        return f'http://bugzilla.{self.sub_domain}.org/rest/bug?'


class BugScraper(object):
    """
    simple Scraper that scrapes bugzilla at a given rate (requests/second)
    """
    def __init__(self, rate):
        self.rate = rate

    def scrape(self, api_url, bug_id):
        wait_time = 1/self.rate
        resp = requests.get(url=api_url, params={'id': bug_id})
        time.sleep(wait_time)
        if resp.ok:
            return resp.json()
        else:
            return None


class BugSaver(object):
    """
    Bug Saver utility that saves bug by years in json lines format
    """
    def __init__(self, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        self.save_dir = save_dir

    def save(self, bug):
        filename = bug['creation_date'].timestamp() + '.jsonl'
        save_path = os.path.join(self.save_dir, filename)
        with open(save_path, 'a') as bdfile:
            bdfile.write(json.dumps(bug) + '\n')
