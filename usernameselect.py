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

from tkinter import *
import subprocess
import logging


class UsernameSelect():
    def __init__(self, master, output_var, remote_host=None):

        logging.info('Initializing UsernameSelect...')
        self.username = str()
        self.remote_host = remote_host
        self.results = list()

        self.get_users(master, output_var, remote_host)

    # If connected to a domain, this will pull all users from the domain.
    # This is a non-issue because how domains are set up and how domain users
    # are not technically local users. However this will also try and find any
    # local users on the machine anyway.
    def _user_list(self):
        if host:
            logging.info('Showing users from "' + host + '"...')
            self.results = subprocess.run(
                ['wmic', '/node:{}'.format(host),
                 'UserAccount', 'get', 'Name,LocalAccount'],
                stdout=subprocess.PIPE).stdout.decode('utf-8').split()
            results = self.results
            for result in results:
                logging.info('Found "' + str(result) + '" user on "' +
                             str(host) + '" !')
            results.sort()
            return results

        # If no connected to a domain, this will have all the local users
        # pulled.
        else:
            logging.info('Showing local users...')
            self.results = subprocess.run(
                ['wmic', 'UserAccount', 'get', 'Name,LocalAccount'],
                stdout=subprocess.PIPE).stdout.decode('utf-8').split()
            results = self.results
            for result in results:
                logging.info('Found "' + str(result) + '" user!')
            results.sort()
            return results

        # Filters out the specified local users and values in array, then
        # appends the rest of values in the array
        for r in results:
            if r in ['Name',
                     'Administrator',
                     'DefaultAccount',
                     'Guest',
                     'WDAGUtilityAccount',
                     'LocalAccount',
                     'TRUE',
                     'FALSE']:
                continue
            self.list_usernames.insert(END, r)

    def get(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        w.destroy()
        # return w.selection_set(0)
        self.username = value
        self.dia_list.destroy()
        logging.info('Selected "' + value + '"!')
        return value

    def get_users(self, master, output_var, host=None):

        self.dia_list = Toplevel(master)
        self.dia_list.title('Select a username from the computer')
        self.dia_list.geometry('200x600')
        self.dia_list.resizable(True, True)
        self.dia_list.grid_columnconfigure(0, weight=1)
        self.dia_list.grid_rowconfigure(0, weight=1)
        self.dia_list.focus()

        self.list_usernames = Listbox(self.dia_list, selectmode=SINGLE)

        if len(self.results) > 0:
            logging.info('Showing user selection prompt!')
            for entry in self.entries:
                self.list_usernames.insert(END, entry['cn'])
        else:
            logging.info('There are no usernames to show!')
            self.list_usernames.insert(END, 'Nothing to see here...')

        self.list_usernames.grid(row=0, column=0, pady=(10, 10), sticky='nswe')
        self.list_usernames.selection_set(first=0)

        self.list_usernames.bind(
            '<Double-Button-1>', lambda e: output_var.set(self.get(e)))
