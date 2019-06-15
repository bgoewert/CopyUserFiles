# Copy User Files

[![Build Status](https://travis-ci.org/bgogurt/CopyUserFiles.svg?branch=master)](https://travis-ci.org/bgogurt/CopyUserFiles)

This was made to copy important files and folders from a Windows user profile to be used on another Windows computer.

## Usage

### Command Line Arguments

These cannot currently be used if using the executable.

|Command            |Description                                                                                                            |
|-------------------|-----------------------------------------------------------------------------------------------------------------------|
|-h, --help         | Displays help message                                                                                                 |
|-d, --destination  | Sets the destination directory (e.g. "C:\\User Folders"). Doing so will allow script to be run silently.              |
|-u, --username     | Sets the username for the source directory to copy files out of (e.g. the user "TestUser" -> "C:\\Users\\TestUser")   |

### Creating an Executable

>Requires PyInstaller

This will create a single executable located in a dist folder that will be created after the PyInstaller .spec file is ran. Using this single executable does not require Python to be installed on a users computer.

```shell
~$ pyi-makespec --onefile app.py
```

Then remove the pathex argument from `a = Analysis()`. This argument is an optional list of paths to be searched before sys.path.

```shell
~$ pyinstaller app.spec
```

[More info on spec files](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
