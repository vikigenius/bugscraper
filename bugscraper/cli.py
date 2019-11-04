# -*- coding: utf-8 -*-

"""Console script for bugscraper."""
import sys
import click


@click.command()
def main(args=None):
    """Console script for bugscraper."""
    click.echo("Replace this message by putting your code into "
               "bugscraper.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


@main.command()
def scrape():
    pass


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
