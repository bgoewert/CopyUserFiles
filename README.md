# Copy User Files

[![Build Status](https://travis-ci.org/bgogurt/CopyUserFiles.svg?branch=master)](https://travis-ci.org/bgogurt/CopyUserFiles)

This was made to copy important files and folders from a Windows user profile to be used on another Windows computer.

## Usage

### Command Line Arguments

These cannot currently be used if using the executable.

|Command Argument   |Description                                                                                                            |
|-------------------|-----------------------------------------------------------------------------------------------------------------------|
|-h, --help         | Displays help message                                                                                                 |
|-d, --destination  | Sets the destination directory (e.g. "C:\\User Folders"). Doing so will allow script to be run silently.              |
|-D, --documents    | Set the remote user's documents folder target location for a new machine.                                             |
|-u, --username     | Sets the username for the source directory to copy files out of (e.g. the user "TestUser" -> "C:\\Users\\TestUser")   |
|-H, --hostname     | Set the remote hostname for target destination                                                                        |

### Building the Executable

>Using this single executable ***does not*** require Python to be installed on a users computer

This will create a `.spec` file that is ran automatically by PyInstaller and creates a single executable located in the `dist` folder.

The `requirements.txt` file is required to install first because this will grab all
dependencies to build the executable.

```shell
> pip install -r requirements.txt
> pyinstaller --onefile --noconsole --name copyuserfiles app.py
```

If you have more than one version of Python installed, make sure to use the desired version of pip and Python when building. Use the `-m PyInstaller` flag in order to build the executable, otherwise it will produce an error.
```shell
> pip3 install -r requirements.txt
> py -m PyInstaller --onefile --noconsole --name copyuserfiles app.py
```

[More info on `.spec` files](https://pyinstaller.readthedocs.io/en/stable/spec-files.html)
