#!/usr/bin/env python3
from xspf_fixup import Playlist, command, option, version
from click import File as FileType
from sys import stdin
from sys import stderr



@command(context_settings=dict(help_option_names=['-h', '--help']))
@option('-v', '--version', 'show_version', is_flag=True,
    help='Show version and exit.')
@option('-i', '--input-file', 'inputfile', 
              help='Input text file (or stdin).',
              type=FileType('r'),
              default=stdin)
def cli(inputfile, show_version=False):
    """A simple command line program to generate a playlist (.xspf file) with a list of files.

    Example:

    $ ls examples/videos/*.mp4 | to_xspf > file.xspf
    
    For more info: (https://github.com/jbokser/xspf_fixup)."""

    if show_version:
        print(version)
        return
    
    pl = Playlist()
    
    with inputfile:
        for line in inputfile.readlines():
            line = line.strip()
            t = pl.add_track(line)
            print(f"File {repr(str(t.path))}: {t.status}", file=stderr)
    print('', file=stderr)

    print(pl)


if __name__ == '__main__':
    cli()
