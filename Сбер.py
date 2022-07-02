import pandas as pd
import time
from os import getcwd
from tkinter import filedialog

filename = filedialog.askopenfilename(initialdir=getcwd())

start = time.time()

with open("Сбер_data.dat") as file:
    # это исключения из сбера, хотя они по бинам подходят
    bin_banks_not_sber = eval(file.readline())
    # три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
    bin_banks = eval(file.readline())

with open(f"Сбер_data{int(start)}.dat", "w") as file:
    # запись исключений из сбера, хотя они по бинам подходят и три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
    file.writelines([str(bin_banks_not_sber)+"\n", str(bin_banks)])



print(f"Считали коды БИН Сбера и исключения, время {int(time.time() - start)}")

# bin_banks_not_sber = ["417367","422838", "431393", "531317", "531344", "533206", "533681", "539013", "545182", "446942", "446915",
#                       "557029", "557030", "557057", "557071", "557072", "557073", "476208", "676261", "485467", "533616"]
#
# bin_banks = ["006", "173", "228", "274", "276", "279", "308", "313", "332", "336", "369", "381", "390", "451", "469", "479",
#              "484", "570", "762", "817", "854", "0220"]

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

# проверяем совпадение кодов сбера и исключений по названиям карт от сбера
df_chk_bin = df[(df["BIN"] == "Другой") & (~df["Продукт"].str.contains("OTHER", regex=False))]
if len(df_chk_bin) > 0:
    # добавить в bin сбера коды
    card_numb = df_chk_bin["Номер карты"].tolist()
    for el in card_numb:
        if el[0:2] == "22": # проверка карт мир
            bin_banks.append(el[2:6])
        else:
            bin_banks.append(el[1:4])
    bin_banks.sort()
    print(f"Найдено {len(df_chk_bin)} новых кодов BIN Сбера")
else:
    print("Новых кодов BIN Сбера в таблице не найдено")

df_chk_bin = df[(df["BIN"] == "Сбербанк") & (df["Продукт"].str.contains("OTHER", regex=False))]
if len(df_chk_bin) > 0:
    card_numb = df_chk_bin["Номер карты"].tolist()
    for el in card_numb:
        bin_banks_not_sber.append(el[0:6])
    bin_banks_not_sber.sort()
    print(f"Найдено {len(df_chk_bin)} новых исключений кодов BIN Сбера")
else:
    print("Новых исключений кодов BIN Сбера в таблице не найдено")

print(f"обработали номера карт на предмет карт Сбера, время {int(time.time() - start)}")

banks_data = pd.pivot_table(df,index=['BIN'], values=['Сумма операции'], aggfunc=[sum,len]) # margins=True
banks_data["% по сумме"] = round(banks_data["sum"]/banks_data["sum"].sum(), 4)
banks_data["% по количеству"] = round(banks_data["len"]/banks_data["len"].sum(), 4)
banks_data.loc['Всего']= banks_data.sum()
banks_data.rename(columns={'sum': 'Сумма операций', 'len': 'Количество операций'}, inplace=True)
cols = list(banks_data.columns.values)
cols = [cols[0], cols[2], cols[1], cols[3]]
banks_data = banks_data[cols]
new_header = [el[0] for el in cols]

print(f"сделали сводную таблицу, время {int(time.time() - start)}")

writer = pd.ExcelWriter("222.xlsx", engine='xlsxwriter')
with writer as file_name:
    df.to_excel(file_name, sheet_name="Sheet0", index=False)
    # banks_data.to_excel(file_name, sheet_name="banks")
    # Convert the dataframe to an XlsxWriter Excel object.
    banks_data.to_excel(file_name, sheet_name="banks", header=False)
    # Get the xlsxwriter objects from the dataframe writer object.
    workbook  = writer.book
    worksheet = writer.sheets["banks"]
    # Add some cell formats.
    format1 = workbook.add_format({'num_format': '#,##0'})
    format2 = workbook.add_format({'num_format': '0%'})
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1})
    worksheet.set_row(0, 30, header_format)
    worksheet.write_row('B1', new_header)
    # Set the column width and format.
    worksheet.set_column('B:B', 15, format1)
    worksheet.set_column('C:C', 10, format2)
    worksheet.set_column('D:D', 15, format1)
    worksheet.set_column('E:E', 10, format2)

    # writer.save()
print(f"записали в файл сводную таблицу, время {int(time.time() - start)}")

with open("Сбер_data.dat", "w") as file:
    # запись исключений из сбера, хотя они по бинам подходят и три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
    file.writelines([str(bin_banks_not_sber)+"\n", str(bin_banks)])

print(f"Записали коды БИН Сбера и исключения, время {int(time.time() - start)}")

end = time.time()
print(f"программа выполнена за {int(end - start)} секунд, записан файл 222.xlsx")