#!/usr/bin/env python3
from click import command, option, argument, ClickException, Choice
from click import Path as TypePath
from bs4 import BeautifulSoup as BS
from urllib.parse import unquote, quote
from pathlib import Path
from os import sep as dirsep
from tabulate import tabulate
from datetime import timedelta

version='0.9b'



class Playlist():


    def __init__(self, filename):
        
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


    def fix_location(self, try_relative_to=True, relative_to='.', search_in='.'):
        results = {}
        for track in self.get_tracks():
            filepath = self.make_filepath(track)
            result = 'Ok'
            if not filepath.is_file():
                result = 'Not Found'
                options = list(Path(search_in).glob('*' + dirsep + filepath.name.strip()))
                if options:
                    result = 'Fixed'
                    option = options[0]
                    new_location = option.absolute()
                    if try_relative_to:
                        try:
                            new_location = option.relative_to(relative_to)
                        except ValueError:
                            pass
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
                            more_keys=[]):

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
        out.append(tabulate(table, headers=headers))
        out.append("")
        results = ', '.join([f"{k}: {v}" for k, v in results.items()])
        out.append(f"Tracks count: ..... {len(table)}{' (' if results else ''}{results}{')' if results else ''}")
        out.append(f"Total duration: ... {cls.timedelta_to_string(total_duration)}")
        out.append("")

        return '\n'.join(out)


    def __str__(self):
        return self.soup.prettify()


    def dump_to_file(self, filename):
        with open(filename, "w") as file:
            print(self, file=file)



@command(context_settings=dict(help_option_names=['-h', '--help']))
@option('-v', '--version', 'show_version', is_flag=True,
    help='Show version and exit')
@argument('command', type=Choice(['show', 'preview', 'fix']))
@argument('filename', type=TypePath(exists=True))
def cli(command, filename, show_version=False):
    """A simple command line program to fix playlist (.xspf files) with broken links."""

    if show_version:
        print(version)
        return
    
    try:
        pl = Playlist(filename)
    except ValueError as e:
        raise ClickException(str(e))
    
    if command=='show':
        print(pl.make_pretty_summary(pl.get_summary()))
        return

    pl.fix_titles()
    summary = pl.fix_location()
    print(pl.make_pretty_summary(summary))
    
    if command=='preview':
        return
    
    pl.dump_to_file(filename)


    
if __name__ == '__main__':
    cli()
