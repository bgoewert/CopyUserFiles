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

import copy_user_files
import tkinter as tk

root = tk.Tk()
root.title('Copy User Files')
root.geometry('720x540')
root.minsize(300, 300)
root.resizable(True, True)

# tkinter string values
str_src_dir = tk.StringVar()
str_dest_dir = tk.StringVar()
str_username = tk.StringVar()

# tkinter integers and booleans
bool_copy_downloads = tk.IntVar()


def header():
    """ Header frame """

    fra_header = tk.Frame(root)
    fra_header.grid_columnconfigure(0, weight=0)
    fra_header.grid_columnconfigure(1, weight=1)
    fra_header.grid_rowconfigure(1, weight=1)

    # Main control group
    grp_controls = tk.LabelFrame(fra_header)
    grp_controls.grid(row=0, column=0, pady=(0, 5), sticky='w')

    # source directory
    src_dir_label = tk.Label(grp_controls, text='Source Directory: ', )
    src_dir_entry = tk.Entry(grp_controls, textvariable=str_src_dir)
    src_dir_btn = tk.Button(grp_controls,
                            text='Select Source Directory',
                            command=lambda: tk.filedialog.askdirectory())
    src_dir_label.grid(row=0, column=0, sticky='e')
    src_dir_entry.grid(row=0, column=1, columnspan=2, sticky='we')
    src_dir_btn.grid(row=0, column=2, sticky='w')

    # Copy Downloads checkbox
    chk_copy_downloads = tk.Checkbutton(grp_controls,
                                        text='Copy Downloads Folder (Limited' +
                                             ' to 50 most recent files)',
                                        variable=bool_copy_downloads)
    chk_copy_downloads.grid(row=1, column=0, columnspan=2, sticky='w')

    # Start button
    btn_start = tk.Button(grp_controls,
                          text='Start')
    btn_start.grid(row=2, column=0, sticky='w')

    # Pack all the widgets
    fra_header.pack(side='top', padx=10, pady=10, fill='x')


def body():
    """ Body frame """

    fra_body = tk.Frame(root, height=20)
    txt_results = tk.Text(fra_body, width=20, height=5)
    txt_results_scroll = tk.Scrollbar(fra_body,
                                      orient='vertical',
                                      command=txt_results.yview)
    txt_results.config(state='disabled', yscrollcommand=txt_results_scroll.set)

    # Pack all the widgets
    fra_body.pack(side='top', fill='both', expand=True)


def footer():
    """ Footer frame """

    fra_footer = tk.Frame(root, height=15)
    fra_footer.grid_columnconfigure(0, weight=1)
    fra_footer.grid_rowconfigure(0, weight=1)

    lbl_version = tk.Label(fra_footer, text='Ver: ' +
                                            copy_user_files.__version__)
    lbl_version.grid(row=0, column=0)

    # Pack all the widgets
    fra_footer.pack(side='bottom')


def app():
    """ The main UI and application """

    header()

    body()

    footer()


if __name__ == "__main__":
    app()
    root.mainloop()
