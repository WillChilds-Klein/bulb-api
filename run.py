#!/usr/bin/env python

import click
import pytest
import sys

from bulb_api import app


@click.group()
@click.pass_context
def cli(ctx):
    """ A command line interface for local development of the bulb API. """
    pass


@cli.command()
@click.option('--port', '-p', default=8080, help='port to serve on')
def prod(port):
    """ Run the bulb API locally """
    app.run(port=port, host='0.0.0.0')


@cli.command()
@click.option('--debug/--no-debug', default=True, help='run in debug mode')
@click.option('--port', '-p', default=8080, help='port to serve on')
def local(debug, port):
    app.run(host='localhost', port=port, debug=debug)


@click.group(invoke_without_command=True)
@click.option('-d', '--test-dir', default='./tests', help='dir w/ pytests')
@click.pass_context
def test(ctx, test_dir):
    """ Execute tests and manage testing infrastructure. """
    ctx.test_dir = test_dir
    # TODO support pytest opts/args.
    #      see http://click.pocoo.org/5/commands/#custom-multi-commands
    if not ctx.invoked_subcommand:
        ctx.invoke(unit)    # by default, run the unit tests


@test.command()
@click.pass_context
def unit(ctx):
    test_dir = ctx.parent.test_dir
    exit_code = pytest.main([test_dir])
    sys.exit(exit_code)


@click.group()
@click.option('--stage', '-s', default='local', help='which stage to manage')
def db():
    """ Manage database(s). """
    pass


@db.command()
def run():
    """ Run db instance locally. """
    pass


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


cli.add_command(test)
cli.add_command(db)
cli.add_command(s3)


if __name__ == '__main__':
    cli()
