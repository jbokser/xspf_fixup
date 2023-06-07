# $ xspf_fixup

A simple command line program to fix playlist (`.xspf` files) with broken links.



## Refrences

* [Source code in Github](https://github.com/jbokser/xspf_fixup)
* [Package from Python package index (PyPI)](https://pypi.org/project/xspf_fixup)



## Requirements

* Python 3.6+



## Installation



### From the Python package index (PyPI)

Run:

```shell
$ pip3 install xspf_fixup
```



### From source

Download from [Github](https://github.com/jbokser/xspf_fixup)

Standing inside the folder, run:

```shell
$ pip3 install -r requirements.txt
```

For install the dependencies and then run:

```shell
$ pip3 install .
```



## Usage

```shell
user@host:~/tmp/xspf_fixup/examples$ xspf_fixup --help
Usage: xspf_fixup [OPTIONS] [FILES]...

  A simple command line program to fix playlist (.xspf files) with broken
  links.

  For more info: (https://github.com/jbokser/xspf_fixup).

Options:
  -v, --version    Show version and exit.
  -s, --show       Show .xspf file info and exit.
  -o, --overwrite  Overwrite the .xspf file.
  -r, --report     Make a report in markdown for each .xspf file.
  -h, --help       Show this message and exit.
user@host:~/tmp/xspf_fixup/examples$ xspf_fixup -o ./test.xspf 

   Title             Duration    Location                     Result
-- ----------------  ----------  ---------------------------  --------
 1 Rockland Agus     03:01       videos/Rockland Agus.mp4     Fixed
 2 Honky Tonk Way    04:06       videos/Honky Tonk Way.mp4    Fixed
 3 Forge Ahead Agos  03:24       videos/Forge Ahead Agos.mp4  Fixed

Tracks count: ..... 3 (Fixed: 3)
Total duration: ... 10:32

user@host:~/tmp/xspf_fixup/examples$
```


```shell
user@host:~/tmp/xspf_fixup/examples$ to_xspf -h
Usage: to_xspf [OPTIONS]

  A simple command line program to generate a playlist (.xspf file) with a
  list of files.

  Example:

  $ ls examples/videos/*.mp4 | to_xspf.py > file.xspf

  For more info: (https://github.com/jbokser/xspf_fixup).

Options:
  -v, --version              Show version and exit.
  -i, --input-file FILENAME  Input text file (or stdin).
  -h, --help                 Show this message and exit.
user@host:~/tmp/xspf_fixup/examples$ ls videos/*.mp4 | to_xspf > files.xspf
File 'videos/Forge Ahead Agos.mp4': Ok
File 'videos/Honky Tonk Way.mp4': Ok
File 'videos/Rockland Agus.mp4': Ok

user@host:~/tmp/xspf_fixup/examples$
```



## Why? (The rationale behind this)

Mainly used by [me](https://github.com/jbokser) to fix the `.xspf` files that *Luis "la cosa muerta" Musa* gave me.



## Author

[Juan S. Bokser](https://github.com/jbokser) <juan.bokser@gmail.com>
