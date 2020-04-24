import click

from lib.logs import LOG_LEVELS, setup_logging
from lib.printer import Printer

CLI_PROG = 'printed'
CLI_VERS = '0.0.0'


@click.command()
@click.version_option(prog_name=CLI_PROG, version=CLI_VERS)
@click.option(
    '-v', '--level', 'level', envvar='LEVEL',
    type=click.Choice(LOG_LEVELS.keys(), case_sensitive=True),
    default='warning', show_default=True,
    help='Control logging level',
)
def main(**cargs):
    setup_logging(cargs['level'])

    printer = Printer()
    if not printer.present:
        click.secho('Printer not found, check connection!', fg='red')
        return
    click.secho(f'Printer found: {printer}', fg='green')


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
