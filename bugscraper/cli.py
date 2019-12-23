# -*- coding: utf-8 -*-

"""Console script for bugscraper."""
import sys
import click
import logging
from pathlib import Path
from bugscraper.log import configure_logger
from bugscraper.bugscraper import BugzillaBugApi, BugSaver
from bugscraper.bugscraper import BugzillaCommentApi, CommentSaver
from bugscraper.bugscraper import BugzillaHistoryApi, HistorySaver
from bugscraper import utils
from tqdm import tqdm


@click.option(
    '-v', '--verbose',
    count=True, help='verbosity level : v{WARN}, vv{INFO}, vvv{DEBUG}'
)
@click.option(
    u'--debug-file', type=click.Path(), default=None,
    help=u'File to be used as a stream for DEBUG logging',
)
@click.group()
def main(verbose, debug_file):
    """Console script for bugscraper."""
    verbosity = [
        'ERROR',
        'WARN',
        'INFO',
        'DEBUG'
    ]
    configure_logger(
        stream_level=verbosity[verbose],
        debug_file=debug_file,
    )
    return 0


year_maps = {
    'kernel': range(2002, 2020),
    'freebsd': range(1994, 2020),
    'mozilla': range(1997, 2020)
}


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@click.option('--init-id', '-i', default=1)
@click.option('--fin-id', '-f', default=200000)
@click.option('--syo', type=click.IntRange(2000, 2020), help='Starting Year range override')
@click.option('--eyo', type=click.IntRange(2000, 2020), help='Ending Year range override')
@click.option('--chunk-size', '-c', default=1000)
@main.command()
def bugscrape(subdomain, save_dir, init_id, fin_id, syo, eyo, chunk_size):
    save_dir = Path(save_dir, subdomain + 'bugs')
    bug_range = range(init_id, fin_id)
    bug_chunks = list(utils.divide_chunks(bug_range, chunk_size))
    api = BugzillaBugApi(subdomain)
    if syo is not None and eyo is not None:
        saver = BugSaver(save_dir, range(syo, eyo + 1))
    else:
        saver = BugSaver(save_dir, year_maps[subdomain])

    for chunk in tqdm(bug_chunks, desc='Fetching and Saving bug chunks of size {}'.format(len(bug_chunks))):
        bug_list = api.fetch(chunk)
        if bug_list is not None:
            saver.save(bug_list)

    saver.save_metadata()


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def commentscrape(subdomain, save_dir):
    save_dir = Path(save_dir, subdomain + 'bugs')

    saver = CommentSaver(save_dir)
    api = BugzillaCommentApi(subdomain)

    for idx, bug_info in enumerate(tqdm(saver.bug_metadata, desc='Fetching and Saving comments')):
        comment_list = api.fetch(bug_info.bug_id)
        if comment_list is not None:
            saver.save(idx, comment_list)

    saver.save_metadata()


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def historyscrape(subdomain, save_dir):
    save_dir = Path(save_dir, subdomain + 'bugs')

    saver = HistorySaver(save_dir)
    api = BugzillaHistoryApi(subdomain)

    for idx, bug_info in enumerate(tqdm(saver.bug_metadata, desc='Fetching and Saving histories')):
        comment_list = api.fetch(bug_info.bug_id)
        if comment_list is not None:
            saver.save(idx, comment_list)

    saver.save_metadata()


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def metagen(save_dir):
    save_dir = Path(save_dir, 'subdomain' + 'bugs')
    CommentSaver(save_dir).save_metadata()


@click.argument('metadata', type=click.Choice(['history', 'comments', 'all']))
@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def clean(metadata, subdomain, save_dir):
    logger = logging.getLogger('bugscraper')
    save_dir = Path(save_dir, subdomain + 'bugs')
    glob = '*' if metadata == 'all' else f'**/*{metadata}.jsonl'
    for match in list(save_dir.glob(glob)):
        logger.info(f'Removing file {match}')
        match.unlink()


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def filter(subdomain, save_dir):
    save_dir = Path(save_dir, subdomain + 'bugs')
    filter_save_dir = Path(save_dir, subdomain + 'bugs_filtered')
    saver = BugSaver(filter_save_dir, year_maps[subdomain])
    for bug in tqdm(utils.mozilla_filter(save_dir), desc='Filtering Bugs'):
        saver.save([bug])


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
