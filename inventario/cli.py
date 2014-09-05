import os
import click
from alembic import context

from . import app, db


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
    from .parsing import Book

    click.echo('Reading: ' + click.format_filename(filename))

    book = Book(filename)

    for page in book.pages:
        click.echo('\nParsing page n: {} name: {}  elements: {}\n'
                   .format(page.n, page.name, len(page.entries)))
        for data in page.entries:
            click.echo('{}\t{}\t{}'.format(data['pos'], data['book_id'], data))


@data.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('first_page', type=int, default=0, required=False)
@click.argument('second_page', type=int, default=None, required=False)
def diff(filename, first_page, second_page):
    from .parsing import Book

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
        click.secho('{}\t{}'.format(id_, new_page.entries_by_id[id_][0]['title']), fg='green')

    click.echo('\nRemoved: {}'.format(removed))
    for id_ in removed:
        click.secho('{}\t{}'.format(id_, old_page.entries_by_id[id_][0]['title']), fg='red')

    click.echo('\nUnchanged: {}'.format(removed))
    for id_ in unchanged:
        click.secho('{}\t{}\t|\t{}'.format(
            id_, old_page.entries_by_id[id_][0]['title'], new_page.entries_by_id[id_][0]['title']))


@data.command('load')
@click.argument('filename', type=click.Path(exists=True))
def data_load(filename):
    """Load data from excel file"""
    from . import parsing, models

    excel = parsing.Book(filename)

    for page in excel.pages:
        listing = models.Listing(id=page.n, year=page.n)
        for entry in page.entries:
            book = models.Book.get_or_create(
                id=entry['book_id'], identified=entry.pop('identified'))

            book_entry = models.BookEntry(listing=listing, book=book, **entry)

            book.last_entry = book_entry
            if not book.first_entry:
                book.first_entry = book_entry

        click.secho('Loaded {} with {} entries'.format(
            listing, len(listing.entries)), fg='green')

        db.session.add(listing)
        db.session.commit()


@data.command('view')
def data_view():
    """List all database data"""
    import json
    from .models import Listing

    n = 0
    for listing in Listing.query:
        for entry in listing.entries:
            n += 1
            click.echo({k: v for k, v in entry.__dict__.items()
                        if not k.startswith('_')})

    if n:
        click.secho('Total {} entries'.format(n))
    else:
        click.secho('No data')


@data.command()
def backout():
    """Delete all previously loaded data"""
    from .models import BookEntry, Book, Listing

    entries, books, listings =\
     BookEntry.query.count(), Book.query.count(), Listing.query.count()

    if not entries and not books and not listings:
        click.secho("No data to delete", fg='green')
        return

    click.secho("""Deleting all imported data:
{} Listings
{} Books
{} BookEntries
""".format(listings, books, entries), fg='red')

    if not click.confirm('Are you sure?'):
        click.secho('Aborted', fg='red')
        return

    BookEntry.query.delete()
    Listing.query.delete()
    Book.query.delete()
    db.session.commit()

    click.secho('Deleted', fg='green')


def _here():
    return os.path.dirname(os.path.realpath(__file__))


@main.command()
@click.argument('argv', nargs=-1)
def database(argv):
    import alembic.config

    click.secho('Database: ' + app.config['SQLALCHEMY_DATABASE_URI'], fg='yellow')

    config = alembic.config.Config(file_=os.path.join(_here(), 'migrations/alembic.ini'))
    config.set_main_option('script_location', os.path.join(_here(), 'migrations'))
    config.set_main_option('sqlalchemy.url', app.config['SQLALCHEMY_DATABASE_URI'])

    cmd = alembic.config.CommandLine('inv database')
    cmd.run_cmd(config, cmd.parser.parse_args(argv))
