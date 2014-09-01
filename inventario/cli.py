import os
import click
from alembic import context

from . import app, db
from .parsing import ID, TITLE, POS, Book, Page


@click.group()
def main():
    click.secho('Configuration file: '
                + click.format_filename(app.config.path), fg='yellow')


@main.group()
def data():
    pass


@data.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('page', type=int, default=None, required=False)
def list(filename, page=None):
    click.echo('Reading: ' + click.format_filename(filename))

    book = Book(filename)

    for page in book.pages:
        click.echo('\nParsing page n: {} name: {}  elements: {}\n'
                   .format(page.n, page.name, len(page.entries)))
        for data in page.entries:
            click.echo('{}\t{}\t{}'.format(data[POS], data[ID], data))


@data.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('first_page', type=int, default=0, required=False)
@click.argument('second_page', type=int, default=None, required=False)
def diff(filename, first_page, second_page):
    click.secho('Reading: ' + click.format_filename(filename))

    book = Book(filename)

    if second_page is None:
        second_page = first_page + 1

    if first_page >= book.npages or second_page >= book.npages:
        raise click.ClickException(
            'Page out of bounds (0, {})'.format(book.npages - 1))

    old_page, new_page = book.page(first_page), book.page(second_page)

    click.echo('Page {}: {} entries'.format(first_page, len(old_page.entries)))
    click.echo('Page {}: {} entries'.format(second_page, len(new_page.entries)))

    added, removed, unchanged = old_page.diff(new_page)

    click.echo('\nAdded: {}'.format(added))
    for id_ in added:
        click.secho('{}\t{}'.format(id_, new_page.entries_by_id[id_][0][TITLE]), fg='green')

    click.echo('\nRemoved: {}'.format(removed))
    for id_ in removed:
        click.secho('{}\t{}'.format(id_, old_page.entries_by_id[id_][0][TITLE]), fg='red')

    click.echo('\nUnchanged: {}'.format(removed))
    for id_ in unchanged:
        click.secho('{}\t{}\t|\t{}'.format(
            id_, old_page.entries_by_id[id_][0][TITLE], new_page.entries_by_id[id_][0][TITLE]))


def _here():
    return os.path.dirname(os.path.realpath(__file__))


@main.command()
@click.argument('argv', nargs=-1)
def database(argv):
    import alembic.config

    click.secho('Database: ' + app.config['SQLALCHEMY_DATABASE_URI'], fg='yellow')

    config = alembic.config.Config()
    config.set_main_option('script_location', os.path.join(_here(), 'migrations'))
    config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

    cmd = alembic.config.CommandLine('inv database')
    cmd.run_cmd(config, cmd.parser.parse_args(argv))
