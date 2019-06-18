# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2019 Brennan Goewert

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

import os
import sys
import shutil
import argparse
import logging
import winreg
from fnmatch import fnmatch

__version__ = '1.3.0'

# Registry Key for User Folders
regKey_UserFolderLocations = ('Software\\Microsoft\\Windows\\CurrentVersion' +
                              '\\Explorer\\User Shell Folders')

# Path for log file
log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        '{}.log'.format(__name__))
# Logging config
logging.basicConfig(level=logging.INFO,
                    filename=log_path,
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler())

# Command-line arguments
argp = argparse.ArgumentParser(description='Copies all the important ' +
                               'files and folders from the user profile.')
# Destination
argp.add_argument('-d', '--destination', type=str,
                  help='Set the destination directory.',
                  action='store',
                  required=False)
# Username
argp.add_argument('-u', '--username', type=str,
                  help='Set the user\'s name of the ' +
                       'profile folder to copy from.',
                  action='store',
                  required=False)
# Set Documents Target Location
argp.add_argument('-D', '--documents', type=str,
                  help='Set the remote user\'s documents folder ' +
                       'target location for a new machine.',
                  action='store',
                  required=False)

# Set remote hostname
argp.add_argument('-H', '--hostname', type=str,
                  help='Set the remote hostname. ' +
                       'Do not set this to use local machine.',
                  action='store',
                  required=False)


def getUserRegKey(key, valName, target=None):
    """ Returns a user registry key value.
    - key
        The registry key (e.g. 'Software\\Microsoft\\Windows\\Current\
Version\\Explorer\\User Shell Folders')
    - valName
        The registry value name
    - target
        The remote target hostname. If None, use local host.
    """

    try:
        # Connect to the registry
        reg = winreg.ConnectRegistry(target, winreg.HKEY_CURRENT_USER)
        # Open key to read
        regKey = winreg.OpenKey(reg, key, 0, winreg.KEY_READ)
    except WindowsError:
        logging.exception(
            'User registry key does not exist: {}'.format(key))
        return None

    # Get key value and type
    keyValue, keyType = winreg.QueryValueEx(regKey, valName)

    # Close opened key
    winreg.CloseKey(regKey)

    return keyValue


def setUserRegKey(key, valName, val, keyType=winreg.REG_SZ, target=None):
    """ Sets a user registry key/value pair.
    - key
        The registry key (e.g. 'Software\\Microsoft\\Windows\\Current\
Version\\Explorer\\User Shell Folders')
    - valName
        The registry value name
    - val
        The new value
    - keyType
        Defaults to REG_SZ
    - target
        The remote target hostname. If None, use local host.
    """

    try:
        # Connect to the registry
        reg = winreg.ConnectRegistry(target, winreg.HKEY_CURRENT_USER)
        # Open key to read
        regKey = winreg.OpenKey(reg, key, 0, winreg.KEY_ALL_ACCESS)
    except WindowsError:
        logging.exception(
            'User registry Key does not exist: {}'.format(key))

    try:
        # Get key current value and type
        keyValue, keyType = winreg.QueryValueEx(regKey, valName)
    except WindowsError:
        logging.info('User registry key does not exist: {}'.format(
            key + os.sep + valName))

    try:
        # Set new key value and get new key value
        winreg.SetValueEx(regKey, valName, 0, keyType, val)
        keyNewValue = winreg.QueryValueEx(regKey, valName)[0]
    except WindowsError:
        logging.exception(
            'An error occurred while ' +
            'setting registry key/value: {}'.format(key))

    # Close opened key
    winreg.CloseKey(regKey)

    logging.info('User registry key set: {}'.format(
        key + os.sep + valName + ' = ' + keyNewValue))
    return keyNewValue


def setMyDocumentsLocation(newLocation, hostname=None):
    """ Set the location for My Documents.
    - newLocation
        The actual new target location to set the Documents folder to.
    - hostname
        The computer name where to set the new documents target location.
    """

    # Get the current location for My Documents
    curVal_myDocuments = getUserRegKey(regKey_UserFolderLocations,
                                       'Personal',
                                       hostname)

    """ Set the new locations for My Documents
    'This PC' Documents GUID Key Name = {F42EE2D3-909F-4907-8871-4C22FC0BF756}
    Quick Access Documents Key Name = Personal
    """
    newVal_personal = setUserRegKey(regKey_UserFolderLocations,
                                    'Personal',
                                    newLocation,
                                    target=hostname)
    newVal_documents = setUserRegKey(regKey_UserFolderLocations,
                                     '{F42EE2D3-909F-4907-8871-4C22FC0BF756}',
                                     newLocation,
                                     target=hostname)

    # TODO(Brennan): Log off then back in to PC after setting the new location


def getUserName(tries=0):
    """
    Returns the username from command line argument or user input.
    Fails after 5 attempts of retriving a valid user.
    """

    logging.info('Attempting to retrieve username...')
    username = None

    # Get any command line arguments
    args = argp.parse_known_args(sys.argv[1:])

    try:
        # 5 total attempts before quitting
        if tries < 5:
            # If username is set as an argument
            if args[0].username is not None:
                username = args[0].username
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep +
                            username)
                if not os.path.exists(homepath):
                    print('That was not a folder...')
                    print(homepath)
                    print('Run the script again to try another user name...')
                    logging.error('User folder not ' +
                                  'found! - {}'.format(homepath))
                    argparse.ArgumentParser.exit()
            # If it is not set as an argument, ask for user input
            else:
                username = input('Name of user folder: ')
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep +
                            username)
                if not os.path.exists(homepath):
                    print('That was not a folder...')
                    print(homepath)
                    logging.error('User folder not ' +
                                  'found! - {}'.format(homepath))
                    getUserName(tries + 1)

        # Failure to find folder after 5 attempts
        else:
            print('YOU HAVE TRIED THIS TOO MANY TIMES!!! (ノಠ益ಠ)ノ彡┻━┻')
            logging.warning('Too many attempts to find ' +
                            'a user folder.')
            quit()

    except:
        logging.exception(str('Something really bad happened trying to get ' +
                              'a folder name, check stacktrace to see the ' +
                              'logs (＃ﾟДﾟ)').encode('utf-8'))
        sys.exit(1)

    # Return the username if folder was found
    logging.info('User profile selected: %s' % username)
    return username


def getUserSrcDir(tries=0):
    """ Returns the user source directory """

    userDir = None

    args = argp.parse_known_args(sys.argv[1:])

    try:
        if tries < 5:
            if args[0].destination is not None:
                userDir = os.path.abspath(args[0].destination)
                if os.path.isfile(userDir):
                    print('That was not a folder...')
                    argparse.ArgumentParser.exit()

            else:
                userDir = os.path.abspath(input('User source folder to copy' +
                                                ' user files/folders from: '))
                if os.path.isfile(userDir):
                    print('That was not a folder...')
                    print(userDir)
                    getUserSrcDir(tries+1)
        else:
            print('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!! (ノಠ益ಠ)ノ彡┻━┻')
            logging.warning('Too many attempts to select ' +
                            'a user destination directory.')
            quit()

    except:
        logging.exception(str('Something really bad happened trying to get ' +
                              'a folder name, check stacktrace to see the ' +
                              'logs (＃ﾟДﾟ)').encode('utf-8'))
        sys.exit(1)

    logging.info('User source directory selected: %s' % userDir)
    return userDir


def getUserDestDir(tries=0):
    """ Returns the user destination directory """

    destDir = None

    args = argp.parse_known_args(sys.argv[1:])

    try:
        # 5 total attempts before quitting
        if tries < 5:
            # Source Directory is declared as an argument
            if args[0].destination is not None:
                destDir = os.path.abspath(args[0].destination)
                if os.path.isfile(destDir):
                    logging.warning('That was not a folder...')
                    argparse.ArgumentParser.exit()

            # Source Directory is not declared as an argument
            else:
                destDir = os.path.abspath(input('Destination folder to copy' +
                                                ' user files/folders to: '))
                # If destination is a file
                if os.path.isfile(destDir):
                    logging.warning('That was not a folder... \n Folder:' +
                                    destDir)
                    getUserDestDir(tries + 1)

        # Failure to find file after 5 attempts
        else:
            logging.exception('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!!' +
                              '(ノಠ益ಠ)ノ彡┻━┻')
            quit()
        # Error handling
    except:
        logging.exception(str('Something really bad happened trying to get ' +
                              'a folder name, check stacktrace to see the ' +
                              'logs (＃ﾟДﾟ)').encode('utf-8'))
        sys.exit(1)

    logging.info('User destination directory selected: %s' % destDir)
    return destDir


def getDocsLoc():
    """ Get the new Documents location. """

    args = argp.parse_known_args(sys.argv[1:])

    docLoc = ''

    # Documents Directory is declared as an argument
    if args[0].documents is not None:
        docLoc = os.path.abspath(args[0].documents)
        if os.path.isfile(docLoc):
            logging.warning('That was not a folder...')
            argparse.ArgumentParser.exit()

    # Documents Directory is not declared as an argument
    else:
        docLoc = input('Documents target location ' +
                       '(leave blank to skip): ')
        # If destination is a file
        if os.path.isfile(docLoc) and docLoc != '':
            logging.warning('That was not a folder... \n Folder:' +
                            docLoc)
            getDocsLoc(tries + 1)

    return docLoc


def getHostname():
    """ Get the remote hostname. Leave blank to use local machine."""

    args = argp.parse_known_args(sys.argv[1:])

    # Documents Directory is declared as an argument
    if args[0].hostname is not None:
        hostname = args[0].hostname

    # Documents Directory is not declared as an argument
    else:
        hostname = input('Hostname: ')

    logging.info('Target Hostname: {}'.format(hostname))
    return hostname


def setDocsLoc(hostname, documents_location, tries=0):
    """ Sets the new Documents target location. """

    try:
        # 5 total attempts before quitting
        if tries < 5:

            # Change the documents folder target location to
            # whatever was specified
            if documents_location != '':
                setMyDocumentsLocation(documents_location, hostname)
                logging.info('Documents target location: {}'.format(
                    documents_location))

            return documents_location

        # Failure to find file after 5 attempts
        else:
            logging.exception('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!!' +
                              '(ノಠ益ಠ)ノ彡┻━┻')
            sys.exit(1)
        # Error handling
    except:
        logging.exception(str('Something really bad happened trying to get ' +
                              'a folder name, check stacktrace to see the ' +
                              'logs (＃ﾟДﾟ)').encode('utf-8'))
        sys.exit(1)


def _findfile(pattern, path):
    """ Finds a file in a folder based on a pattern search.
    (e.g. '*.pst')
    """
    result = []

    # Finding all files in the specified path to search
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result


def _copyall(src, dst):
    """ Copies all sub folders and files from the source. """

    try:
        for root, dirs, files in os.walk(src):
            # Creates the root directory
            if not os.path.isdir(root):
                os.makedirs(root)
                logging.info('Root directory created: %s' % root)

            # Creates directories and files to be copied into
            for f in files:
                # Creates directories if destination does not have a directory
                if not os.path.isdir(dst):
                    os.makedirs(dst)
                    logging.info('Destination directory created: %s' % dst)

                # Copies the files
                nf_path = os.path.join(dst, f)
                f_path = os.path.join(root, f)
                shutil.copy(f_path, nf_path)
                logging.info('New file copied: %s' % str(nf_path))

    # Any error during the copying process
    except Exception as err:
        logging.exception('Exception occurred while trying to copy')
        sys.exit(1)


def copyuserfiles(username, dest, src=None, hostname=None):
    """ Copies the files from the profile folder of the defined username to
    the destination folder. All files and subfolders will be placed in a
    folder with the same name as the username.

    - username
        The name of the user profile folder
    - dest
        The destination directory to copy the user files to.

    """

    # Folders to copy over
    folders = [
        '\\Documents',
        '\\Desktop',
        '\\Favorites',
        '\\Pictures',
        '\\Videos',
        '\\AppData\\Local\\Microsoft\\Outlook',
        '\\AppData\\Roaming\\Microsoft\\Outlook',
        '\\AppData\\Roaming\\Microsoft\\Outlook\\RoamCache',
        '\\AppData\\Roaming\\Microsoft\\Signatures',
        '\\AppData\\Local\\Mozilla\\Firefox',
        '\\AppData\\Roaming\\Mozilla\\Firefox',
        '\\AppData\\Local\\Google\\Chrome'
    ]

    if src:
        for f in folders:
            folders[folders.index(f)] = f.replace(
                'C:', '\\\\{}\\C$'.format(src))

    # Copy all paths in the folders array
    for path in folders:
        path = os.path.abspath(path)

        if hostname:
            newDst = path.replace(os.sep.join(path.split(os.sep)[:3]),
                                  dest + os.sep + '%s' % username)
        else:
            newDst = path.replace(os.sep.join(path.split(os.sep)[:3]),
                                  dest + os.sep + '%s' % username)

        # Copy Outlook folders in %APPDATA%/Local/Microsoft/Outlook
        if 'Outlook' in path and 'Local' in path:
            for f in _findfile('*.pst', path):
                _copyall(f, os.path.join(newDst, f))

        # Copy Outlook folders in %APPDATA%/Roaming/Microsoft/Outlook
        elif ('Outlook' in path and
              'RoamCache' not in path and
              'Roaming' in path):
            for f in _findfile('*.nk2', path):
                _copyall(f, os.path.join(newDst, f))

        else:
            _copyall(path, newDst)


if __name__ == '__main__':
    try:
        logging.info('****************************************************')
        logging.info('SCRIPT STARTED')
        logging.info('****************************************************')
        logging.info('* This script does not copy anything ' +
                     'from the downloads folder. *')
        logging.info('Arguments: {}'.format(
            argp.parse_known_args(sys.argv[1:])))
        host = getHostname()
        setDocsLoc(hostname=host,
                   documents_location=getDocsLoc())
        copyuserfiles(username=getUserName(),
                      dest=getUserDestDir(),
                      hostname=host)
        logging.info('****************************************************')
        logging.info('SCRIPT STOPPED')
        logging.info('****************************************************')
    except (KeyboardInterrupt,
            SystemError,
            SystemExit) as err:
        logging.error("Stopped the script!", exc_info=True)
        logging.info('****************************************************')
        sys.exit(1)
