from setuptools import setup, find_packages
from os.path    import dirname, abspath

name = 'xspf_fixup'
base_dir = dirname(abspath(__file__))

with open(base_dir + "/README.md", "r") as file_:
    long_description = file_.read()

version = None
with open(base_dir + "/" + name + ".py", "r") as file_:
    for l in file_.readlines():
        if 'version' in l and '=' in l:
            d = {}
            exec(l, {}, d)
            if 'version' in d:
                version = d['version']
                break
if not version:
    raise(Exception('No version defined!'))

requirements = []
requires_files = ["/requirements.txt",
                  "/" + name + ".egg-info/requires.txt"]
for file_path in requires_files:
    try:
        with open(base_dir + file_path, "r") as file_:
            for p in file_.read().split():
                if p not in requirements:
                    requirements.append(p)
    except FileNotFoundError:
        pass
if not requirements:
    raise(Exception('Empty requirements!'))

setup(
    name=name ,
    version=version,
    packages=find_packages(),
    author='Juan S. Bokser',
    author_email='juan.bokser@gmail.com',
    description='A simple command line program to fix playlist (.xspf files) with broken links.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    scripts=['xspf_fixup', 'xspf_fixup.py']
)
