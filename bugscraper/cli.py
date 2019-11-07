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


year_maps = {
    'kernel': range(2002, 2019)
}


@click.argument('subdomain')
@click.option('--save_dir', '-s', type=click.Path(), default='.')
@click.option('--init_id', '-i', default=1)
@click.option('--fin-id', '-f', default=200000)
@click.option('--syo', type=click.IntRange(2000, 2020), help='Starting Year range override')
@click.option('--eyo', type=click.IntRange(2000, 2020), help='Ending Year range override')
@main.command()
def scrape(subdomain, save_dir, init_id, fin_id, syo, eyo):
    save_dir = PurePath(save_dir, 'bugs')
    api = BugzillaBugApi(subdomain)
    if syo is not None and eyo is not None:
        saver = BugSaver(save_dir, range(syo, eyo))
    else:
        saver = BugSaver(save_dir, year_maps[subdomain])
    for bug_id in tqdm(range(init_id, fin_id), desc='Fetching Issues'):
        bug = api.get_bug(bug_id)
        if bug is not None:
            saver.save(bug)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
