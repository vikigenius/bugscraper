# -*- coding: utf-8 -*-

"""Console script for bugscraper."""
import sys
import click
from pathlib import PurePath
from tqdm import tqdm
from bugscraper.log import configure_logger
from bugscraper.bugscraper import BugzillaBugApi, BugSaver


@click.option(
    '-v', '--verbose',
    is_flag=True, help='Print debug information', default=False
)
@click.option(
    u'--debug-file', type=click.Path(), default=None,
    help=u'File to be used as a stream for DEBUG logging',
)
@click.group()
def main(verbose, debug_file):
    """Console script for bugscraper."""
    configure_logger(
        stream_level='DEBUG' if verbose else 'INFO',
        debug_file=debug_file,
    )
    return 0


@click.argument('subdomain')
@click.option('--save_dir', '-s', type=click.Path(), default='.')
@click.option('--init-id', '-i', default=1)
@click.option('--fin-id', '-f', default=200000)
@main.command()
def scrape(subdomain, save_dir, init_id, fin_id):
    save_dir = PurePath(save_dir, 'bugs')
    api = BugzillaBugApi(subdomain)
    saver = BugSaver(save_dir)
    for bug_id in tqdm(range(init_id, fin_id), desc='Fetching Issues'):
        bug = api.get_bug_with_comments(bug_id)
        if bug is not None:
            saver.save(bug)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
