import click

from lib.labels import LABELS
from lib.logs import LOG_LEVELS, setup_logging
from lib.printer import Printer

CLI_PROG = 'printed'
CLI_VERS = '0.0.0'


@click.command()
@click.version_option(prog_name=CLI_PROG, version=CLI_VERS)
@click.argument(
    'image', envvar='IMAGE',
    type=click.File(mode='rb', lazy=False),
)
@click.option(
    '-l', '--label', 'label_name', envvar='LABEL',
    type=click.Choice(LABELS.keys(), case_sensitive=False),
    default='62', show_default=True,
    help='Specify labels size (width in millimeters)',
)
@click.option(
    '-r', '--rotate', 'rotate', envvar='ROTATE',
    type=int, default=0, show_default=True,
    help='Rotate image counter clock wise before printing',
)
@click.option(
    '-t', '--threshold', 'threshold', envvar='THRESHOLD',
    type=float, default=70.0, show_default=True,
    help='Threshold (percent) to differentiate between black and white pixels',
)
@click.option(
    '-d', '--dither', 'dither', envvar='DITHER',
    is_flag=True, default=False, show_default=True,
    help='Apply dithering to the image - threshold has no effect',
)
@click.option(
    '-p', '--preview', 'preview', envvar='PREVIEW',
    is_flag=True, default=False, show_default=True,
    help='Do not print, but open generated image as preview',
)
@click.option(
    '-v', '--level', 'level_name', envvar='LEVEL',
    type=click.Choice(LOG_LEVELS.keys(), case_sensitive=False),
    default='warning', show_default=True,
    help='Control logging level',
)
def main(image, preview, **cargs):
    setup_logging(cargs['level_name'].lower())

    printer = Printer()
    if not preview and not printer.present(silent=True):
        click.secho('Printer not found, check connection!', fg='red')
        return
    click.secho(f'Using Printer: {printer}', fg='green')

    label = LABELS.get(cargs['label_name'].lower())
    click.secho(f'Using label: {label}', fg='green')

    printer(
        image=image,
        label=label,
        preview=preview,
        dither=cargs['dither'],
        rotate=cargs['rotate'],
        threshold=cargs['threshold']
    )


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    main()
