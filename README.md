<h1 align="center">extraire</h1>

<p align="center">
<a href="https://github.com/beerpiss/extraire/actions">
    <img alt="Actions Status"
      src="https://img.shields.io/github/workflow/status/beerpiss/extraire/build%20extraire?style=flat-square">
</a>
<a href="https://github.com/psf/black">
    <img alt="Code style: black"
         src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square">
</a>
<a href="https://github.com/beerpiss/extraire/blob/trunk/LICENSE">
    <img alt="License: 0BSD"
    src="https://img.shields.io/static/v1?label=License&message=0BSD&color=brightgreen&style=flat-square">
</a>
<a href="https://pypi.org/project/extraire/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/extraire?style=flat-square">
</a>
<img alt="Supported Python versions: 3.6.2, 3.7, 3.8, 3.9, 3.10"
     src="https://img.shields.io/pypi/pyversions/extraire?style=flat-square">
</p>

> extraire (verb): to extract

Simple program to dump onboard SHSH blobs with a valid generator for **jailbroken** iOS
devices. Supports Windows, macOS and Linux.

## What's this?
This program dumps the IMG4 ApTicket from /dev/disk1 on the device, copies it to your
computer and converts it to a valid SHSH blob, no external dependencies required.

Even though the dumped SHSH blob is valid, you will still be limited by a few factors:
- SEP/Baseband/Rose firmware compatibility with the currently signed iOS version
- If you've updated to your current iOS version with the Settings app, you cannot use
the dumped blob without a bootROM exploit (e.g. checkm8).

## Requirements
OpenSSH Server installed on your jailbroken device. That's it!

## Installation
### From PyPI
```
pip install -U extraire
```
### Standalone binaries
Standalone binaries for Windows, macOS and Linux can be found
[here.](https://github.com/beerpiss/extraire/releases/tag/v0.1.4)

You will need to allow executable permission for macOS and Linux after downloading.
Run `chmod +x /path/to/extraire` in a terminal (replace `/path/to/extraire` with the
actual path).

## Usage
Run `extraire` only for an interactive guide.

```
❯ extraire --help
usage: extraire [-h] [-p PASSWORD] [-o OUTPUT] [--non-interactive] [HOST[:PORT]]

positional arguments:
  HOST[:PORT]           The device's IP address

optional arguments:
  -h, --help            show this help message and exit
  -p PASSWORD, --password PASSWORD
                        The device's root user password
  -o OUTPUT, --output OUTPUT
                        Where to save the dumped blob
  --non-interactive     Don't interactively ask for missing value
                        (assume default if missing)
```

## Running/building from source
Clone this repo, install the dependencies with `poetry install` or `pip install .`, and
run `python3 -m extraire`

To build a wheel, do `poetry build`.

## Credits
[tihmstar](https://github.com/tihmstar): without his
[img4tool](https://github.com/tihmstar/img4tool) code I wouldn't be able to write code
for dealing with IMG4s in Python.
