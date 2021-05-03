#!/usr/bin/python
# -*- coding: utf-8 -*-

# импортирование модулей python
import tkinter as tk

def menu_command(name_win):
    child = tk.Toplevel(window)
    child.title(name_win)
    child.geometry(f'220x190+{window.winfo_x()+10}+{window.winfo_y()+10}') #+400+300

    languages = ["Python", "JavaScript", "C#", "Java", "C/C++", "Swift",
                 "PHP", "Visual Basic.NET", "F#", "Ruby", "Rust", "R", "Go",
                 "T-SQL", "PL-SQL", "Typescript"]
    fr_verx = tk.Frame(child)
    fr_verx.pack(side=tk.TOP, fill=tk.BOTH)
    fr_niz = tk.Frame(child)
    fr_niz.pack(side=tk.BOTTOM, fill=tk.BOTH)

    sb = tk.Scrollbar(fr_verx)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    bot_ok = tk.Button(fr_niz, text = "  ОК  ", width=10)
    bot_ok.pack(side=tk.LEFT)
    bot_can = tk.Button(fr_niz, text="Отмена", width=10)
    bot_can.pack(side=tk.RIGHT)

    languages_listbox = tk.Listbox(fr_verx, yscrollcommand=sb.set, selectmode=tk.SINGLE, cursor= ,width=50, height=10)

    for language in languages:
        languages_listbox.insert(tk.END, language)

    languages_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    sb.config(command=languages_listbox.yview)

    child.grab_set()
    child.focus_set()
    child.wait_window()

def menu_command_easy():
    menu_command("Простые")



window = tk.Tk()
window.title("Добро пожаловать в приложение PythonRu")
window.geometry('400x250')
menu = tk.Menu(window)
new_item = tk.Menu(menu, tearoff=0)
one_item = tk.Menu(menu, tearoff=0)
new_item.add_command(label='Простые', command = menu_command_easy)
# new_item.add_separator()
new_item.add_command(label='Средние')
new_item.add_command(label='Сложные')
menu.add_cascade(label='Загрузить схему', menu=new_item)
menu.add_cascade(label='Настройки', menu=one_item)
one_item.add_command(label='Показывать')
one_item.add_command(label='Скрыть')
window.config(menu=menu)



window.mainloop()



