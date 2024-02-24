# Copy User Files

[![Build Status](https://travis-ci.org/bgogurt/CopyUserFiles.svg?branch=master)](https://travis-ci.org/bgogurt/CopyUserFiles)

## Deprecated!

> This project has been out of date for some time and is no longer being used. I currently do not have time to keep updated.
> 
> Brennan 2024-02-24

## Description

This was made to copy important files and folders from a Windows user profile to be used on another Windows computer.

PyInstaller was chosen to be used to freeze everything into a distributable package. Using this executable *does not* require Python to be installed on a user's computer. For more information on how to use it, visit the [PyInstaller Documentation](https://pyinstaller.readthedocs.io/en/stable)

**Table of Contents**
- [Usage](#Usage)
  - [Building an Executable](#Building-an-Executable)
    - [CLI](#CLI)
      - [Command Line Arguments](#Command-Line-Arguments)
    - [GUI](#GUI)
    - [Using with mulitiple Python versions](#Using-with-mulitiple-Python-versions)

&nbsp;

## Usage

&nbsp;

### Building an Executable

The CLI commands below will create a single executable located in a `dist` folder that is created by PyInstaller. The `requirements.txt` file is required to install first in order to grab all dependencies before building the package.

&nbsp;

#### CLI

```shell
> pip install -r requirements.txt
> pyinstaller --onefile copyuserfiles.py
```

##### Command Line Arguments

> These unfortunately cannot currently be used if using the executable just yet.

|Command Argument   |Description                                                                                                                    |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------|
|-h, --help         | Displays help message                                                                                                         |
|-s, --source       | Sets the source directory (e.g. "C:\\Users\\profile")                                                                         |
|-d, --destination  | Sets the destination directory where the profile folder will be copied to. Doing so will allow script to be run silently.     |
|-D, --documents    | Set the remote user's documents folder target location for a new machine.                                                     |
|-u, --username     | Sets the username for the source directory to copy files out of (e.g. the user "TestUser" -> "C:\\Users\\TestUser")           |
|-H, --hostname     | Set the remote hostname for target destination                                                                                |

&nbsp;

#### GUI

```shell
> pip install -r requirements.txt
> py pyinstaller --onefile --noconsole --name copyuserfiles app.py
```

#### Using with mulitiple Python versions

If you have more than one version of Python installed (i.e. 2.7 and 3.x), make sure to use the desired version of pip and Python when building. Use the `-m PyInstaller` flag in order to build the executable, otherwise it will produce an error.

For Python 3:
```shell
> pip3 install -r requirements.txt
> py -m PyInstaller --onefile --noconsole --name copyuserfiles app.py
```
