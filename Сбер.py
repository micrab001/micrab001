import pandas as pd
import time
from os import getcwd
from tkinter import filedialog

filename = filedialog.askopenfilename(initialdir=getcwd())

start = time.time()
bin_banks_not_sber = ["417367","422838", "531317","533681","539013", "545182", "446942", "446915", "557029", "557030", "557057", "557071", "557072",
                      "557073", "476208"]
bin_banks = ["173", "228", "274", "276", "279", "308", "313", "332", "336", "369", "390", "451", "469", "479", "484", "570", "762", "817", "854", "0220"]

def convert_data(val):
    return val.date()

def convert_bin(val):
    if val[0:2] == "22": # проверка карт мир
        bin = val[2:6]
    else:
        bin = val[1:4]
    if bin in bin_banks:
        if val[0:6] not in bin_banks_not_sber:
            return "Сбербанк"
        else:
            return "Другой"
    else:
        return "Другой"

df = pd.read_excel(pd.ExcelFile(filename), "Sheet0")
print(f"чтение файла данных, время {int(time.time() - start)}")
for col in df.columns:
    if col not in ['Дата операции', 'Дата выгрузки в АБС', 'Сумма операции',
       'Сумма комиссии', 'Сумма расчета']:
        df[col] = df[col].astype("str")
        df[col] = df[col].apply(lambda x: "" if x == "nan" else x )
    print(f"обработка колонки {col} завершена, время {int(time.time() - start)}")
print(f"обработка колонок завершена, время {int(time.time() - start)}")
df.insert(df.columns.get_loc('Дата операции')+1,'Дата операции магазин', df["Дата операции"].apply(convert_data))
print(f"добавили дату операции в магазине, время {int(time.time() - start)}")
df.insert(df.columns.get_loc('Продукт')+1,'BIN', df["Номер карты"].apply(convert_bin))
print(f"обработали номера карт на предмет карт Сбера, время {int(time.time() - start)}")

banks_data = pd.pivot_table(df,index=['BIN', ], values=['Сумма операции'], aggfunc=[sum,len]) # margins=True
banks_data["% по сумме"] = round(banks_data["sum"]/banks_data["sum"].sum(), 4)
banks_data["% по количеству"] = round(banks_data["len"]/banks_data["len"].sum(), 4)
banks_data.loc['Всего']= banks_data.sum()
banks_data.rename(columns={'sum': 'Сумма', 'len': 'Количество'}, inplace=True)


print(f"сделали сводную таблицу, время {int(time.time() - start)}")

with pd.ExcelWriter("222.xlsx") as file_name:
    df.to_excel(file_name, sheet_name="Sheet0", index=False)
    banks_data.to_excel(file_name, sheet_name="banks")
print(f"записали в файл сводную таблицу, время {int(time.time() - start)}")
end = time.time()
print(f"программа выполнена за {int(end - start)} секунд, записан файл 222.xlsx")