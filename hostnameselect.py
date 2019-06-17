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
import ldap3
import logging
import os

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


def hostname_select_dialog():

    dia_hostname_select = tk.Toplevel()
    dia_hostname_select.title('Select a remote hostname')
    dia_hostname_select.focus()
    dia_hostname_select.geometry('200x600')
    dia_hostname_select.resizable(True, True)
    dia_hostname_select.grid_columnconfigure(0, weight=1)
    dia_hostname_select.grid_rowconfigure(0, weight=1)

    str_server = tkSimpleDialog.askstring(
        'Input',
        'Domain Controller Hostname/IP',
        parent=dia_hostname_select)
    str_domain = tkSimpleDialog.askstring(
        'Input',
        'Domain',
        parent=dia_hostname_select,
        initialvalue=getfqdn().split('.', 1)[1])
    str_user = tkSimpleDialog.askstring(
        'Input',
        'Username',
        parent=dia_hostname_select,
        initialvalue=os.getlogin())
    str_pass = tkSimpleDialog.askstring(
        'Input',
        'Password',
        parent=dia_hostname_select,
        show='*')

    comp_list = ad.getComputerList(str_server,
                                   str_domain,
                                   str_user,
                                   str_pass)

    list_hostnames = tk.Listbox(dia_hostname_select, selectmode=tk.SINGLE)

    for comp in comp_list:
        list_hostnames.insert(tk.END, comp['cn'])

    list_hostnames.grid(row=0, column=0, pady=(10, 10), sticky='nswe')
    list_hostnames.selection_set(first=0)

    list_hostnames.bind('<<ListboxSelect>>',
                        lambda e: print(e.widget.selection_set(0)))


class HostnameSelect():
    def __init__(self, master):

        self.server = None
        self.conn = None
        self.entries = list()
        self.hostname = str()
        self.__setattr__('entries', list())

        if len(self.__getattribute__('entries')) == 0:
            self._ad_login(master)
        else:
            self.entries = self.__getattribute__('entries')

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

        try:
            domain = getfqdn().split('.', 1)[1]
            entry_domain.insert(0, domain)
        except:
            dia_login.destroy()
            return logging.exception('Failed to get a domain name.')

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
                                     dia_login.destroy()])

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

    def _ad_connect(self, server, domain, usr, pwd):

        self.srv = ldap3.Server(server, get_info=ldap3.ALL)
        self.conn = ldap3.Connection(self.srv,
                                     user='{}\\{}'.format(domain, usr),
                                     password=pwd,
                                     authentication=ldap3.NTLM)

        if not self.conn.bind():
            messagebox.showerror('Login Failed',
                                 'Failed to connect to Active Directory')
            raise ConnectionError('Failed to connect to Active Directory',
                                  self.conn.result)
        else:
            self.entries = self._ad_computerlist()
            self.conn.unbind()
            return self.entries

    def _ad_computerlist(self):
        try:
            self.conn.search(self.srv.info.naming_contexts[0],
                             '(&(objectclass=computer)' +
                             '(!(operatingSystem=*Server*)))',
                             attributes=['cn', 'dNSHostName'])
            return self.conn.entries
        except:
            return logging.exception('Failed to search for computers.')

    def get(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        w.destroy()
        # return w.selection_set(0)
        self.hostname = value
        self.dia_list.destroy()
        return value

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
            self.__setattr__('entries', self.entries)

            for entry in self.entries:
                self.list_hostnames.insert(END, entry['cn'])
        else:
            self.list_hostnames.insert(END, 'Nothing to see here...')

        self.list_hostnames.grid(row=0, column=0, pady=(10, 10), sticky='nswe')
        self.list_hostnames.selection_set(first=0)

        self.list_hostnames.bind(
            '<Double-Button-1>', lambda e: output_var.set(self.get(e)))
