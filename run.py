#!/usr/bin/env python

import click
import sys

from api import app


@click.group()
def cli():
    """ A command line interface for local development of the bulb API. """
    pass


@cli.command()
@click.option('--port', '-p', default=8080, help='port to serve on')
@click.option('--debug/--no-debug', default=True, help='run in debug mode')
def local(port, debug):
    """ Run the bulb API locally """
    app.run(port=port, host='0.0.0.0')


@click.group()
@click.option('--stage', '-s', default='local', help='which stage to manage')
def db():
    """ Manage database(s). """
    pass


@db.command()
def run():
    """ Run db instance locally. """
    pass


cli.add_command(db)


@db.command()
def init():
    """ Initialize database schema. """
    pass


@db.command()
def status():
    pass


@db.command()
def teardown():
    """ Destroy database schema. """
    pass


@click.group()
def s3():
    """ Manage S3 and static assets. """
    pass


cli.add_command(s3)


if __name__ == '__main__':
    cli()
