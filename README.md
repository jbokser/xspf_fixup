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
Usage: xspf_fixup [OPTIONS] {show|preview|fix} FILENAME

  A simple command line program to fix playlist (.xspf files) with broken
  links.

Options:
  -v, --version  Show version and exit
  -h, --help     Show this message and exit.
user@host:~/tmp/xspf_fixup/examples$ xspf_fixup fix ./test.xspf 

Title             Duration    Location                     Result
----------------  ----------  ---------------------------  --------
Rockland Agus     03:01       videos/Rockland Agus.mp4     Fixed
Honky Tonk Way    04:06       videos/Honky Tonk Way.mp4    Fixed
Forge Ahead Agos  03:24       videos/Forge Ahead Agos.mp4  Fixed

Tracks count: ..... 3 (Fixed: 3)
Total duration: ... 10:32

user@host:~/tmp/xspf_fixup/examples$  
```



## Why? (The rationale behind this)

Mainly used by [me](#author) to fix the `.xspf` files that *Luis "la cosa muerta" Musa* gave me.



## Author

Juan S. Bokser <juan.bokser@gmail.com>
