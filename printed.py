import sys

import click

CLI_PROG = 'printed'
CLI_VERS = '0.0.0'


@click.command()
@click.version_option(prog_name=CLI_PROG, version=CLI_VERS)
def main():
    return 0


if __name__ == '__main__':
    sys.exit(main())
