# Слияние файлов за месяц (или несколько) по ИП Огнева от сбербанка. Файлы должны лежать в одной директории

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
        df_all = pd.concat([df_all, pd.read_excel(pd.ExcelFile(file_name), sheet_name=0, skiprows=2)], ignore_index=True)
    else:
        df_all = pd.read_excel(pd.ExcelFile(file_name), sheet_name=0, skiprows=2)
        flag = True
    print(f"обработан файл {file_name}")
df_all = df_all.loc[df_all['Мерчант (совершения операции)'] == '851000086896']
df_all['ИНН предприятия'] = "771002957898"
df_all['Наименование предприятия'] = "ИП Огнева Е.П."
df_all.to_excel("Огнева.xlsx", sheet_name="Sheet0", index=False)




