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
from fnmatch import fnmatch

# Global vars
__version__ = '1.2.0'

# Logging
log_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'copy_user_files.log')
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

# Function to retrieves username from input
def getUserName(tries=0):
    logging.info('Attempting to retrieve username...')
    username = None

    # Retrieving arguments
    args = argp.parse_known_args(sys.argv[1:])
    logging.info(args)
    try:
        # 5 total attempts before quitting
        if tries < 5:

            # Username is declared as an argument
            if args[0].username is not None:
                logging.info('Username is declared as an argument!')
                username = args[0].username
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep + username)
                if not os.path.exists(homepath):
                    logging.warning('That was not a folder...')
                    logging.warning('Folder:' + homepath)
                    input('Try another user name...')
                    argparse.ArgumentParser.exit()

            # Username is not declared as an argument
            else:
                logging.info('Prompting for user name...')
                username = input('Name of user folder: ')
                homepath = (os.path.dirname(os.environ['HOME']) +
                            os.sep + username)
                if not os.path.exists(homepath):
                    logging.warning('That was not a folder...')
                    logging.warning('Folder: ' + homepath)
                    getUserName(tries+1)

        # Failure to find file after 5 attempts
        else:
            print('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!! (ノಠ益ಠ)ノ彡┻━┻')
            logging.warning('Too many attempts to define ' +
                            'a user folder.')
            quit()
    except:
        logging.exception(str('Something bad just happened, check stacktrace' +
                          ' to see the logs (＃ﾟДﾟ)').encode('UTF-8'))
    logging.info('User profile selected: %s' % username)
    return username

# Function to set destination directory to copy into
def getUserDir(tries=0):
    userDir = None

    args = argp.parse_known_args(sys.argv[1:])

    try:
        # 5 total attempts before quitting
        if tries < 5:
            # Source Directory is declared as an argument
            if args[0].destination is not None:
                userDir = os.path.abspath(args[0].destination)
                if os.path.isfile(userDir):
                    logging.warning('That was not a folder...')
                    argparse.ArgumentParser.exit()

            # Source Directory is not declared as an argument
            else:
                userDir = os.path.abspath(input('Destination folder to copy' +
                                                ' user files/folders to: '))
                # If destination is a file
                if os.path.isfile(userDir):
                    logging.warning('That was not a folder... \n Folder:' + userDir)
                    getUserDir(tries+1)

        # Failure to find file after 5 attempts
        else:
            logging.exception('YOU HAVE ALREADY TRIED THIS FIVE TIMES!!!' + 
                            '(ノಠ益ಠ)ノ彡┻━┻', exc_info=True)
            sys.exit(1)
        # Error handling
    except Exception as err:
        logging.exception('Something really bad happened trying to get a folder ' +
                        'name, check stacktrace to see the logs (＃ﾟДﾟ)', exc_info=True)

    logging.info('User destination directory selected: %s' % userDir)
    return userDir

# Finding files
def findfile(pattern, path):
    result = []

    # Finding all files in the specified path to search
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch(name, pattern):
                result.append(os.path.join(root, name))

    return result

# Copy function
def copy(src, dst):
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
        logging.exception('Exception occurred trying to copy', exc_info=True)

# Main function
def app():
    print('\n* This script does not copy ' +
          'anything from the downloads folder. *\n')

    # * Vars for script *
    # getUserName() runs a function to retrieve a username whether by an argument
    # or by the prompt inside the function and returns the username as a string
    #
    # getDir() runs a function to select a directory to copy all the files in the
    # selected users folder whether by an argument or a prompt inside the 
    # function and returns the destination directory as a string 
    username = getUserName()
    userDir = getUserDir()

    # Folders to copy over
    folders = [
        r'C:\Users\%s\Documents' % username,
        r'C:\Users\%s\Desktop' % username,
        r'C:\Users\%s\Favorites' % username,
        r'C:\Users\%s\Pictures' % username,
        r'C:\Users\%s\Videos' % username,
        r'C:\Users\%s\AppData\Local\Microsoft\Outlook' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Outlook' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Outlook\RoamCache' % username,
        r'C:\Users\%s\AppData\Roaming\Microsoft\Signatures' % username,
        r'C:\Users\%s\AppData\Local\Mozilla\Firefox' % username,
        r'C:\Users\%s\AppData\Roaming\Mozilla\Firefox' % username,
        r'C:\Users\%s\AppData\Local\Google\Chrome' % username
        ]

    # Looking for paths to copy
    for path in folders:
        path = os.path.abspath(path)
        newDst = path.replace(os.sep.join(path.split(os.sep)[:3]),
                              userDir + os.sep + '%s' % username)

        # Copy Outlook folders in %APPDATA%/Local/Microsoft/Outlook
        if 'Outlook' in path and 'Local' in path:
            for f in findfile('*.pst', path):
                copy(f, os.path.join(newDst, f))

        # Copy Outlook folders in %APPDATA%/Roaming/Microsoft/Outlook
        elif ('Outlook' in path and
              'RoamCache' not in path and
              'Roaming' in path):
            for f in findfile('*.nk2', path):
                copy(f, os.path.join(newDst, f))

        else:
            copy(path, newDst)


if __name__ == '__main__':
    try:
        logging.info('****************************************************')
        logging.info('SCRIPT STARTED')
        logging.info('****************************************************')
        app()
        logging.info('****************************************************')
        logging.info('SCRIPT STOPPED')
        logging.info('****************************************************')
    except (KeyboardInterrupt, SystemError, SystemExit) as err:
        logging.error("Stopped the script!", exc_info=True)
        logging.info('****************************************************')
        sys.exit(1)

