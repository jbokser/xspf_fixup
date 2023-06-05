#!/usr/bin/env python3
from click import command, option, argument, ClickException, BadParameter
from click import Path as TypePath
from bs4 import BeautifulSoup as BS
from urllib.parse import unquote, quote
from pathlib import Path
from os import chdir
from tabulate import tabulate
from datetime import timedelta
from contextlib import contextmanager
from warnings import filterwarnings


version='0.9.3b1'



# Filter BeautifulSoup warnings
filterwarnings("ignore", category=UserWarning)



@contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    chdir(path)
    try:
        yield
    finally:
        chdir(prev_cwd)



class Playlist():


    def __init__(self, filename):

        self.filename = filename
        content = []

        with open(filename, "r") as file:
            content = file.readlines()

        content = "".join(content)
        self.soup = BS(content, features="xml")

        if not list(self.get_tracks()):
            raise ValueError('Empty playlist or wrong format file')


    def get_tracks(self):
        for location in self.soup.find_all('location'):
            if location.parent.name == 'track':
                track = location.parent
                yield(track)


    @staticmethod
    def make_filepath(track):
        return Path(unquote(track.location.string.strip()))


    @classmethod
    def make_title(cls, track):
        filepath = cls.make_filepath(track)
        return ' '.join(filepath.stem.split())


    def fix_titles(self, rewrite_all=True):
        for track in self.get_tracks():
            new_title = self.make_title(track)
            if track.title:
                if not rewrite_all:
                    new_title = track.title.string
                track.title.extract()
            track.insert(0, self.soup.new_tag('title'))
            track.title.string = new_title
        return self.get_summary()


    def fix_location(self, try_relative_to=True, search_in='.'):

        results = {}

        relative_to = Path(self.filename).absolute().parent

        for track in self.get_tracks():

            filepath = self.make_filepath(track)

            result = 'Ok'

            with working_directory(relative_to):
                ok = filepath.is_file() and filepath.exists()

            if not ok :
                result = 'Not Found'
                options = list(Path(search_in).rglob(filepath.name.strip()))
                if options:
                    result = 'Fixed'
                    option = options[0]
                    new_location = option.absolute()
                    if try_relative_to:
                        new_location_lst = list(new_location.parts)
                        relative_to_lst = list(relative_to.parts)
                        while new_location_lst and relative_to_lst:
                            if new_location_lst[0]==relative_to_lst[0]:
                                new_location_lst.pop(0)
                                relative_to_lst.pop(0)
                            else:
                                break
                        new_location_lst = ['..' for x in relative_to_lst] + new_location_lst
                        new_location = Path(*new_location_lst)
                    new_location = quote(str(new_location))
                    track.location.string = new_location
            results[track.location.string] = result
        summary = self.get_summary()

        for t in summary:
            t['result'] = results[t['location']]

        return summary


    @staticmethod
    def timedelta_to_string(td):
        out = str(td)
        if out.startswith('0:'):
            out = out[2:]
        if '.' in out:
            return '.'.join(out.split('.')[:-1])
        return out


    @staticmethod
    def location_to_string(l):
        return unquote(l)


    def get_summary(self):

        keys = ['title', 'duration', 'location']
        out = []

        for track in self.get_tracks():
            reg = {}
            for key in keys:
                value = getattr(track, key, None)
                value = None if value is None else value.string
                if key=='duration' and value:
                    value = timedelta(milliseconds=int(value))
                reg[key] = value
            out.append(reg)

        return out


    @classmethod
    def make_pretty_summary(cls, summary,
                            headers = ['Title', 'Duration', 'Location', 'Result'],
                            keys = ['title', 'duration', 'location', 'result'],
                            more_headers = [],
                            more_keys=[],
                            markdown=False):

        headers += more_headers
        keys += more_keys

        keys_from_summary = []
        for data in summary:
            for key in data.keys():
                if not key in keys_from_summary:
                    keys_from_summary.append(key)
        for k in set(keys).difference(set(keys_from_summary)):
            i = keys.index(k)
            keys.pop(i)
            headers.pop(i)

        table = []
        total_duration = timedelta(0)

        results = {}
        for data in summary:
            reg = []
            for key in keys:
                value = data[key]
                if key=='result':
                    results[value] = results.get(value, 0) + 1
                if key=='location':
                    value=cls.location_to_string(value)
                if key=='duration':
                    if value:
                        total_duration += value
                        value = cls.timedelta_to_string(value)
                    else:
                        value = 'N/A'
                if key=='title':
                    if not value:
                        value = 'N/A'
                reg.append(value)
            table.append(reg)

        out = []
        out.append("")
        out.append(tabulate(table, headers=headers, tablefmt=("github" if markdown else "simple")))
        out.append("")
        results = ', '.join([f"{k}: {v}" for k, v in results.items()])
        if markdown:
            out.append("```")
        out.append(f"Tracks count: ..... {len(table)}{' (' if results else ''}{results}{')' if results else ''}")
        out.append(f"Total duration: ... {cls.timedelta_to_string(total_duration)}")
        if markdown:
            out.append("```")
        out.append("")

        return '\n'.join(out)


    def __str__(self):

        out = self.soup.prettify() #FIXME

        # I need to find a better prettify()
        new_lines = []
        lines = out.split('\n')
        fnc_is_tag = lambda s: s.strip().startswith('<')
        max_i = len(lines) - 1
        for i, l in enumerate(lines):
            
            prev_is_tag = fnc_is_tag(lines[i-1]) if i>0 else True
            next_is_tag = fnc_is_tag(lines[i+1]) if i<max_i else True
            is_tag = fnc_is_tag(l)

            if not is_tag and (next_is_tag or prev_is_tag):
                new_lines.append(l.strip())
            elif is_tag and not prev_is_tag:
                new_lines.append(l.strip())
                new_lines.append('\n')
            elif is_tag and not next_is_tag:
                new_lines.append(l)
            else:
                new_lines.append(l)
                new_lines.append('\n')

        return ''.join(new_lines)


    def dump_to_file(self, filename=None):
        if filename is None:
            filename = self.filename
        with open(filename, "w") as file:
            print(self, file=file)


    def make_report_file(self, filename=None, markdown=True):
        
        if filename is None:
            filename = self.filename

        file_path = Path(filename)
        directory_path = file_path.parent
        file_name_without_extension = file_path.stem

        filename = directory_path.joinpath(
            file_name_without_extension + ('.md' if markdown else '.txt'))

        summary = self.get_summary()
        str_report = self.make_pretty_summary(summary, markdown=markdown)
      
        with open(filename, "w") as file:

            if markdown:
                print(f'# Playlist: {file_name_without_extension}', file=file)
                print('', file=file)
            else:
                title = ('Playlist: ' + str(file_name_without_extension)).strip().split()
                print(' '.join(title), file=file)
                print(' '.join([('=' * len(t)) for t in title]), file=file)

            print(str_report, file=file)

            print('---', file=file)
            if markdown:
                print(f'Report generated with [`xspf_fixup` (v{version})](https://github.com/jbokser/xspf_fixup).', file=file)
            else:
                print(f'Report generated with xspf_fixup v{version} (https://github.com/jbokser/xspf_fixup).', file=file)
            print('', file=file)
    
        return(filename)

            

@command(context_settings=dict(help_option_names=['-h', '--help']))
@option('-v', '--version', 'show_version', is_flag=True,
    help='Show version and exit.')
@option('-s', '--show', 'show', is_flag=True,
    help='Show .xspf file info and exit.')
@option('-o', '--overwrite', 'overwrite', is_flag=True,
    help='Overwrite the .xspf file.')
@option('-r', '--report', 'report', is_flag=True,
    help='Make a report in markdown for each .xspf file.')
@argument('files', nargs=-1, type=TypePath())
def cli(files, show_version=False, show=False, overwrite=False, report=False):
    """A simple command line program to fix playlist (.xspf files) with broken links.
    
    For more info: (https://github.com/jbokser/xspf_fixup)."""

    if show_version:
        print(version)
        return

    if not files:
        raise BadParameter('It is necessary to pass at least one file.')

    filename_list = [f for f in files if Path(f).is_file()]

    if not filename_list:
        raise ClickException('No file found.')
    
    found = False
    duration = timedelta(0)
    for filename in filename_list:
        ok = True
        try:
            pl = Playlist(filename)
        except ValueError as e:
            ok = False
        if ok:
            found = True

            if len(filename_list)>1 and show:
                print(f"File: {filename}")
                print('======' + ('=' * len(filename)))

            if report:
                report_file = pl.make_report_file()

            if show:
                summary = pl.get_summary()
                for d in [x['duration'] for x in summary]:
                    duration += d
                print(pl.make_pretty_summary(summary))

            if report:
                print(f'Report file: {report_file}')
                if len(filename_list)>1 and show:
                    print('')

            if show or report:
                continue

            pl.fix_titles()
            summary = pl.fix_location()
            for d in [x['duration'] for x in summary]:
                duration += d
            print(pl.make_pretty_summary(summary))

            if overwrite:
                pl.dump_to_file()

    if not found:
        raise ClickException('No file found.')

    if duration and len(filename_list)>1:
        print(f"Number of files: ............... {len(filename_list)}")
        print(f"Total duration of all files: ... {Playlist.timedelta_to_string(duration)}")
        print('')



if __name__ == '__main__':
    cli()
