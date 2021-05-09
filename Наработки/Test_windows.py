#!/usr/bin/python
# -*- coding: utf-8 -*-

# импортирование модулей python
import tkinter as tk
from tkinter import messagebox

def menu_command(name_win):
    selection = False

    def command_ok(*args):
        nonlocal selection
        if messagebox.askyesno(f"Зарузка схемы судоку",
                               "Вы действительно хотите загрузить новую схему судоку?"
                               "\nВнимание! Все внесенное ранее в поле судоку будет стерто."):
            selection = l_listbox.curselection()
        child.destroy()

    def command_can():
        child.destroy()

    # создание дочернего окна
    child = tk.Toplevel(window)
    child.title(name_win)
    child.geometry(f'220x190+{window.winfo_x()+10}+{window.winfo_y()+10}') #положение окна на 10 точек смещения от основного окна
    # действия с окном
    if name_win == 'Простые':
        fn = "easy.dat"
    elif name_win == 'Средние':
        fn = "medium.dat"
    elif name_win == 'Сложные':
        fn = "hard.dat"
    elif name_win == 'Очень сложные':
        fn = "very_hard.dat"
    with open(fn) as file_fielsds:
        s_fields = file_fielsds.readlines()
        l_str = [name_win +" №"+str(i)+" "+s_fields[i][:15]+"..." for i in range(len(s_fields))]
    fr_verx = tk.Frame(child)
    fr_verx.pack(side=tk.TOP, fill=tk.BOTH)
    fr_niz = tk.Frame(child)
    fr_niz.pack(side=tk.BOTTOM, fill=tk.BOTH)
    # создание виджета со списком со скролбаром справа
    sb = tk.Scrollbar(fr_verx)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    l_listbox = tk.Listbox(fr_verx, yscrollcommand=sb.set, selectmode=tk.SINGLE, width=50, height=10)
    # наполнение списка листбокса строчками
    for line in l_str:
        l_listbox.insert(tk.END, line)
    # финальная конфигурация листбокса
    l_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    sb.config(command=l_listbox.yview)
    l_listbox.selection_set(first=0)

    # создание кнопок
    bot_ok = tk.Button(fr_niz, text = "  ОК  ", width=10, command=command_ok)
    bot_ok.pack(side=tk.LEFT)
    bot_can = tk.Button(fr_niz, text="Отмена", width=10, command=command_can)
    bot_can.pack(side=tk.RIGHT)

    # возможна реакция на указание на строчку мышкой
    # l_listbox.bind("<<ListboxSelect>>", command_ok)
    l_listbox.bind('<Double-1>', command_ok)
    # эти три строчки делают окно модальным, их надо помещять вниз(в конце) команд
    child.grab_set()
    child.focus_set()
    child.wait_window()

    return (s_fields[selection[0]][:-1], selection[0]) if selection else selection

# реакция на 1 пункт меню
def menu_command_easy():
    digits = menu_command("Простые")
    if digits:
        all_pole = [["-" for i in range(9)] for ii in range(9)]
        for i in range(len(digits[0])):
            all_pole[i // 9][i % 9] =(int(digits[0][i]) if digits[0][i] != "0" else "-")
        print(all_pole)

def menu_command_medium():
    print(menu_command("Средние"))


# создание окна
window = tk.Tk()
window.title("Добро пожаловать в приложение PythonRu")
window.geometry('400x250')

# создание двух пунктов меню с открывающимися списками
menu = tk.Menu(window) # собственно меню
new_item = tk.Menu(menu, tearoff=0) # первый пункт меню
one_item = tk.Menu(menu, tearoff=0) # второй пункт меню
new_item.add_command(label='Простые', command = menu_command_easy) # команда первого меню пункт меню
# new_item.add_separator() # можно добавлять разделительную линию между пунктами меню
new_item.add_command(label='Средние', command = menu_command_medium) # команда первого меню пункт меню
new_item.add_command(label='Сложные') # команда первого меню пункт меню
menu.add_cascade(label='Загрузить схему', menu=new_item) # первый пункт меню название
menu.add_cascade(label='Настройки', menu=one_item) # второй пункт меню название
one_item.add_command(label='Показывать') # команда второго меню пункт меню
one_item.add_command(label='Скрыть') # команда второго меню пункт меню
window.config(menu=menu) # внедрение меню в окно



window.mainloop()



