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
from tkinter import messagebox
from socket import getfqdn
import subprocess
import ldap3
import logging
import os
import __main__


class HostnameSelect():
    def __init__(self, master):

        logging.info('Initializing HostnameSelect...')
        self.server = None
        self.conn = None
        self.entries = list()
        self.hostname = str()
        self._ad_login(master)

    # Login window for AD
    def _ad_login(self, master):

        dia_login = Toplevel(master)
        dia_login.title('Login to Active Directory')
        dia_login.geometry('400x150')
        dia_login.resizable(False, False)
        dia_login.focus()
        dia_login.grab_set()

        lblfra_inputs = LabelFrame(dia_login)
        lblfra_inputs.grid(row=0, column=0, pady=(20, 20), padx=(10, 10))
        lblfra_inputs.grid_columnconfigure(0, weight=0)
        lblfra_inputs.grid_columnconfigure(1, weight=1)
        lblfra_inputs.place(anchor='c', relx=.5, rely=.5)

        # Labels
        label_server = Label(lblfra_inputs,
                             text='Domain Controller Hostname/IP')
        label_domain = Label(lblfra_inputs, text='Domain Name')
        label_user = Label(lblfra_inputs, text='Domain Admin Username')
        label_pass = Label(lblfra_inputs, text='Domain Admin Password')

        # Entries
        entry_server = Entry(lblfra_inputs)
        entry_domain = Entry(lblfra_inputs)
        entry_user = Entry(lblfra_inputs)
        entry_pass = Entry(lblfra_inputs, show='*')

        logging.info('Showing AD login prompt!')

        # From information from computer, automatically input credentials
        try:
            # Domain
            domain = getfqdn().split('.', 1)[1]
            entry_domain.insert(0, domain)

            # Logon Server
            server = subprocess.run(['cmd', '/c', 'echo %logonserver%'],
                                    stdout=subprocess.PIPE)
            logonserver = server.stdout.decode('utf-8').replace('\\\\', '')

            entry_server.insert(0, logonserver)

            # Username
            username = os.getlogin()
            entry_user.insert(0, username)

        # If cannot find one, leave it be
        except:
            dia_login.destroy()
            logging.exception('Failed to get a domain name.')
            return

        # TODO(Brennan): See if a keep alive is possible
        # check_keepalive = Checkbutton(dia_login, text='Stay logged in?')

        # Action buttons
        button_login = Button(lblfra_inputs,
                              text='Login',
                              command=lambda: (
                                  dia_login.destroy() if
                                  self._ad_connect(entry_server.get(),
                                                   entry_domain.get(),
                                                   entry_user.get(),
                                                   entry_pass.get())
                                  is not None else False))
        button_cancel = Button(lblfra_inputs,
                               text='Cancel',
                               command=lambda: [
                                     dia_login.destroy(),
                                     logging.info('Not connected to AD!')])

        label_server.grid(row=0, column=0, sticky='e', padx=(10, 0))
        label_domain.grid(row=1, column=0, sticky='e', padx=(10, 0))
        label_user.grid(row=2, column=0, sticky='e', padx=(10, 0))
        label_pass.grid(row=3, column=0, sticky='e', padx=(10, 0))

        entry_server.grid(row=0, column=1, sticky='we', padx=(0, 10))
        entry_domain.grid(row=1, column=1, sticky='we', padx=(0, 10))
        entry_user.grid(row=2, column=1, sticky='we', padx=(0, 10))
        entry_pass.grid(row=3, column=1, sticky='we', padx=(0, 10))

        button_login.grid(row=4, column=0)
        button_cancel.grid(row=4, column=1)

    # Connects to domain with credentials
    def _ad_connect(self, server, domain, usr, pwd):

        logging.info('Connecting to domain...')
        self.srv = ldap3.Server(server, get_info=ldap3.ALL)
        self.conn = ldap3.Connection(self.srv,
                                     user='{}\\{}'.format(domain, usr),
                                     password=pwd,
                                     authentication=ldap3.NTLM)
        logging.info('-==- [ LOGIN INFO ] -==-')
        logging.info('user      : ' + usr)
        logging.info('domain    : ' + domain)
        logging.info('server    : ' + server)
        logging.info('-==- [ LOGIN INFO ] -==-')

        # Connection not made to Domain, raise error
        if not self.conn.bind():
            logging.error('Could not connect to domain!')
            messagebox.showerror('Login Failed',
                                 'Failed to connect to Active Directory')
            raise ConnectionError('Failed to connect to Active Directory',
                                  self.conn.result)

        # Connected to domain returns entries and disconnects
        else:
            logging.info('Connected to domain!')
            self.entries = self._ad_computerlist()
            self.conn.unbind()
            return self.entries

    # Searches for computers on AD
    def _ad_computerlist(self):
        try:
            logging.info('Searching for computers on AD...')
            self.conn.search(self.srv.info.naming_contexts[0],
                             '(&(objectclass=computer)' +
                             '(!(operatingSystem=*Server*)))',
                             attributes=['cn', 'dNSHostName'])
            entries = self.conn.entries
            entries.sort()
            entryTotal = 0
            for entry in entries:
                entryTotal = entryTotal + 1
                logging.info('Found "' + str(entry['cn']) + '" in AD!')
            logging.info('Total hostnames: ' + str(entryTotal))
            return entries
        # If something happens, log the exception
        except:
            return logging.exception('Failed to search for computers in AD!')

    def get(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        w.destroy()
        # return w.selection_set(0)
        self.hostname = value
        self.dia_list.destroy()
        logging.info('Selected "' + value + '"!')
        return value

    # Hostname display window
    def get_name(self, master, output_var):

        self.dia_list = Toplevel(master)
        self.dia_list.title('Select a remote hostname')
        self.dia_list.geometry('200x600')
        self.dia_list.resizable(True, True)
        self.dia_list.grid_columnconfigure(0, weight=1)
        self.dia_list.grid_rowconfigure(0, weight=1)
        self.dia_list.focus()

        self.list_hostnames = Listbox(self.dia_list, selectmode=SINGLE)

        if len(self.entries) > 0:
            logging.info('Showing hostnames!')
            for entry in self.entries:
                self.list_hostnames.insert(END, entry['cn'])
        else:
            logging.info('There are no hostnames to show!')
            self.list_hostnames.insert(END, 'Nothing to see here...')

        self.list_hostnames.grid(row=0, column=0, pady=(10, 10), sticky='nswe')
        self.list_hostnames.selection_set(first=0)

        self.list_hostnames.bind(
            '<Double-Button-1>', lambda e: output_var.set(self.get(e)))
