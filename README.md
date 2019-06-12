# Copy User Files

This was made to copy important files and folders from a Windows user profile to be used on another Windows computer.

## Usage

### Command Line Arguments

|Command            |Description                                                                                                |
|-------------------|-----------------------------------------------------------------------------------------------------------|
|-d, --destination  | Sets the destination directory (e.g. "C:\\User Folders"). Doing so will allow script to be run silently.  |
|-u, --username     | Sets the username of the profile folder to copy from.                                                     |

<br>

### Creating an Executable

>Requires PyInstaller

This will create a single executable located in a dist folder that will be created after the PyInstaller .spec file is ran. Using this single executable does not require Python to be installed on a users computer.

```
pyinstaller imgResize.spec
```