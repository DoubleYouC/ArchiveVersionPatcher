'''Archive Version Patcher'''

import tkinter as tk
import json
import logging
import sys
import argparse

from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory
from os import makedirs, listdir
from datetime import datetime
from pathlib import Path

def sm(message, error_message = False, info_message = False, update_status = True):
    #My standard Error message, statusbar update, and logging function
    logging.info(message)
    if error_message:
        messagebox.showerror('Error', message)
    if info_message:
        messagebox.showinfo('Info', message)
    if update_status:
        statusbar['text'] = message
    window.update()

def browse_button():
    btn_browse['state'] = 'disabled'

    file = askopenfilename(title=text['Select archive window'][language.get()], filetypes=[("Bethesda Archive2 files", "*.ba2"), ("All files", "*.*")])
    if file != '':
        btn_browse['text'] = file
        sm(text['Archive selected'][language.get()] + file)
        btn_patch['state'] = 'normal'
        btn_dir['state'] = 'disabled'
    btn_browse['state'] = 'normal'
    window.update()

def dir_button():
    btn_dir['state'] = 'disabled'
    directory = askdirectory(title=text['Select directory window'][language.get()])
    if directory != '':
        btn_dir['text'] = directory
        sm(text['Directory selected'][language.get()] + directory)
        btn_patch['state'] = 'normal'
        btn_browse['state'] = 'disabled'
    btn_dir['state'] = 'normal'
    window.update()

def patch_button():
    #What the patch button does
    btn_patch['state'] = 'disabled'
    if btn_browse['text'] != text['btn_browse'][language.get()]:
        patch_archive(btn_browse['text'])
        btn_browse['text'] = text['btn_browse'][language.get()]
        btn_dir['state'] = 'normal'
    elif btn_dir['text'] != text['btn_dir'][language.get()]:
        i = 0
        list_of_patched_archives = text['Patched archive list'][language.get()]
        base_dir = btn_dir['text']
        for x in listdir(base_dir):
            if x.endswith(".ba2"):
                archive_path = base_dir + '/' + x
                if patch_archive(archive_path):
                    list_of_patched_archives += f'\n{archive_path}'
                    i += 1
        if i > 0:
            sm(list_of_patched_archives, False, True, False)
            sm(str(i) + text['Files successfully patched'][language.get()])
        else:
            sm(base_dir + text['No archives patched'][language.get()], False, True)
        btn_dir['text'] = text['btn_dir'][language.get()]
        btn_browse['state'] = 'normal'



    window.update()

def patch_archive(archive):
    sm(text['Patching archive message'][language.get()] + f' {archive}...')
    patched = False

    try:
        with open(archive, "r+b") as f:
            f.seek(4)
            byte = f.read(1)
            if byte == b'\x07' or byte == b'\x08':
                f.seek(4)
                f.write(b'\x01')
                patched = True
            elif byte == b'\x01':
                sm(archive + text['No patch needed'][language.get()])
            else:
                sm(archive + text['Unexpected version'][language.get()], True)
            f.close()
    except PermissionError:
        sm(text['Permission Error'][language.get()] + archive, True)

    if patched:
        sm(f'{archive} ' + text['Patching archive complete'][language.get()])
    return patched


def change_language(lingo):
    #Language handling
    sm(f'Using {lingo}.', update_status = False)
    window.wm_title(text['title'][language.get()])
    btn_browse['text'] = text['btn_browse'][language.get()]
    btn_dir['text'] = text['btn_dir'][language.get()]
    btn_patch['text'] = text['btn_patch'][language.get()]
    btn_patch['state'] = 'disabled'

if __name__ == '__main__':
    #Console mode
    parser = argparse.ArgumentParser()
    parser.add_argument("-cm", "--consolemode", help="console application mode", action="store_true")
    args = parser.parse_args()

    #Make logs.
    today = datetime.now()
    log_directory_date = today.strftime("%Y %b %d %a - %H.%M.%S")
    my_app_log_directory = f'logs\\{log_directory_date}'
    my_app_log = f'{my_app_log_directory}\\log.log'
    if getattr(sys, 'frozen', False):
        exedir = Path(sys.executable).parent
    else:
        exedir = Path(__file__).parent
    makedirs(my_app_log_directory)
    logging.basicConfig(filename=my_app_log, filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    #Temp file list
    temp_file_list = []

    #translation json
    with Path(exedir).joinpath('translate.json').open(encoding='utf-8') as translate_json:
        text = json.load(translate_json)

    if not args.consolemode:
        #Create base app window
        window = tk.Tk()
        icon = tk.PhotoImage(file=str(Path(exedir).joinpath('Icon.gif')))
        window.tk.call('wm','iconphoto',window._w, icon)

        window.wm_title('BA2 Archive Version Patcher')
        window.minsize(500, 200)

        #Three frames on top of each other to place widgets in
        frame_first = tk.Frame(window)
        frame_second = tk.Frame(window)
        frame_third = tk.Frame(window)

        #Language dropdown
        options = text['languages']
        language = tk.StringVar(window)
        language.set(text['languages'][0])
        optm_language = ttk.OptionMenu(window, language, text['languages'][0], *text['languages'], command=change_language)
        optm_language.pack(padx=5, pady=5)

        #Select Archive button
        btn_browse = tk.Button(frame_first, text=text['btn_browse'][language.get()], command=browse_button)
        btn_browse.pack(anchor=tk.CENTER, padx=10, pady=10)

        #Select Folder button
        btn_dir = tk.Button(frame_first, text=text['btn_dir'][language.get()], command=dir_button)
        btn_dir.pack(anchor=tk.CENTER, padx=10, pady=10)

        #patch button
        btn_patch = tk.Button(frame_third, text=text['btn_patch'][language.get()], command=patch_button)
        btn_patch.pack(anchor=tk.CENTER, padx=10, pady=10)
        btn_patch['state'] = 'disabled'

        #Statusbar
        statusbar = tk.Label(frame_third, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W, wraplength=500)
        statusbar.pack(side=tk.BOTTOM, padx=3, fill=tk.X)

        #Pack frames
        frame_first.pack()
        frame_second.pack()
        frame_third.pack(expand=True, fill=tk.X)

        #Start app
        window.mainloop()
