# -*- coding: utf-8 -*-

"""Console script for bugscraper."""
import sys
import click
from pathlib import PurePath
from bugscraper.log import configure_logger
from bugscraper.bugscraper import BugzillaBugApi, BugSaver, BugzillaCommentApi, CommentSaver
from bugscraper import utils
from tqdm import tqdm


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
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@click.option('--init-id', '-i', default=1)
@click.option('--fin-id', '-f', default=200000)
@click.option('--syo', type=click.IntRange(2000, 2020), help='Starting Year range override')
@click.option('--eyo', type=click.IntRange(2000, 2020), help='Ending Year range override')
@click.option('--chunk-size', '-c', default=1000)
@main.command()
def bugscrape(subdomain, save_dir, init_id, fin_id, syo, eyo, chunk_size):
    save_dir = PurePath(save_dir, 'bugs')
    bug_range = range(init_id, fin_id)
    bug_chunks = list(utils.divide_chunks(bug_range, chunk_size))
    api = BugzillaBugApi(subdomain)
    if syo is not None and eyo is not None:
        saver = BugSaver(save_dir, range(syo, eyo), len(bug_chunks))
    else:
        saver = BugSaver(save_dir, year_maps[subdomain], len(bug_chunks))

    for chunk in tqdm(bug_chunks, desc='Fetching and Saving bug chunks of size {}'.format(len(bug_chunks))):
        bug_list = api.fetch(chunk)
        if bug_list is not None:
            saver.save(bug_list)

    saver.save_metadata()


@click.argument('subdomain')
@click.option('--save-dir', '-s', type=click.Path(), default='.')
@main.command()
def commentscrape(subdomain, save_dir):
    save_dir = PurePath(save_dir, 'bugs')

    saver = CommentSaver(save_dir)
    api = BugzillaCommentApi(subdomain)

    for idx, bug_info in enumerate(tqdm(saver.bug_metadata, desc='Fetching and Saving comments')):
        comment_list = api.fetch(bug_info.bug_id)
        if comment_list is not None:
            saver.save(idx, comment_list)

    saver.save_metadata()


@click.argument('save-dir')
@main.command()
def metagen(save_dir):
    save_dir = PurePath(save_dir, 'bugs')
    CommentSaver(save_dir).save_metadata()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
