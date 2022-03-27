<h1 align="center">Deverser</h2>

<p align="center">
<a href="https://github.com/beerpiss/deverser.py/actions"><img alt="Actions Status" src="https://github.com/beerpiss/deverser.py/actions/workflows/build.yaml/badge.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/beerpiss/deverser.py/blob/main/LICENSE"><img alt="License: 0BSD" src="https://img.shields.io/static/v1?label=License&message=0BSD&color=brightgreen"></a>
</p>

(I need a better name, this is stolen)

Simple program to dump onboard SHSH blobs with a valid generator for iOS devices. Supports Windows, macOS and Linux.

## What's this?
This program dumps iBoot from /dev/disk1 on the device, copies it to your computer and converts it to a valid SHSH blob, no external dependencies required.

Even though the dumped SHSH blob is valid, you will still be limited by a few factors:
- SEP/Baseband/Rose firmware compatibility with the currently signed iOS version
- If you've updated to your current iOS version with the Settings app, you cannot use the dumped blob without a bootROM exploit (e.g. checkm8).

## Requirements
OpenSSH Server installed on your jailbroken device. That's it!

## Usage
- Download the latest stable release for your platform [here.](https://github.com/beerpiss/deverser.py/releases/tag/v0.1.1)
- **(macOS/Linux only)** In a terminal window, type `chmod +x ` (with a trailing space) and drag and drop the downloaded file into the terminal, then hit Enter/Return to run.
- Drag and drop the file into the terminal (again), then hit Enter/Return to run the program.
- You will now be guided by the program.

## Credits
[tihmstar](https://github.com/tihmstar): without his [img4tool](https://github.com/tihmstar/img4tool) code I wouldn't be able to write code for dealing with IMG4s in Python.
