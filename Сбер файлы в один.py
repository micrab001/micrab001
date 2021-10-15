# Слияние файлов за месяц (или несколько) от сбербанка. Файлы должны лежать в одной директории
import os
import pandas as pd
from os import getcwd
from tkinter import filedialog

dirname = filedialog.askdirectory(initialdir=getcwd()).replace("/", chr(92))
all_dir = os.listdir(dirname)
filesnames = [dirname+chr(92)+f for f in all_dir if os.path.isfile(dirname+chr(92)+f) and "xlsx" in f]
flag = False

for file_name in filesnames:
    if flag:
        df_all = pd.concat([df_all, pd.read_excel(pd.ExcelFile(file_name), sheet_name=0)], ignore_index=True)
    else:
        df_all = pd.read_excel(pd.ExcelFile(file_name), sheet_name=0)
        flag = True
    print(f"обработан файл {file_name}")
df_all.rename(columns={'Дата проведения операции': 'Дата операции', 'Карта': 'Номер карты'}, inplace=True)
df_all.to_excel("month.xlsx", sheet_name="Sheet0", index=False)




