import pandas as pd
import time
from os import getcwd
from tkinter import filedialog
import sqlite3
import requests


filename = filedialog.askopenfilename(initialdir=getcwd())

start = time.time()

magazin_baza = {"Галерея": ["Галерея Водолей", 14], "БУМ": ["Марьино БУМ", 132], "Дом 76А": ["Сокол", 104],
                "Отрадное": ["Отрадное", 59], "Семёновская": ["Семеновский", 194], "Коламбус": ["Пражская", 172],
                "МКАД": ["Вегас", 255], "Планерное": ["Планерная", 251], "Витте Молл": ["Бутово", 310],
                "Речной": ["Речной", 247], "Зелёный": ["Новогиреево", 301], "Калейдоскоп": ["Сходненская", 343],
                "Дубравная": ["Митино", 351], "Кунцево": ["Кунцево", 422], "AVENUE": ["Авеню Ю-З", 536],
                "Каширская": ["Каширский", 529]}


def add_magazin(adress: str):
    global magazin_baza
    for mag in magazin_baza:
        if mag in adress:
            return (magazin_baza[mag][0], magazin_baza[mag][1])
    return("не найден", "не найден")


# with open("Сбер_data.dat") as file:
#     # это исключения из сбера, хотя они по бинам подходят
#     bin_banks_not_sber = eval(file.readline())
#     # три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
#     bin_banks = eval(file.readline())
#
# with open(f"Сбер_data{int(start)}.dat", "w") as file:
#     # запись исключений из сбера, хотя они по бинам подходят и три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
#     file.writelines([str(bin_banks_not_sber)+"\n", str(bin_banks)])
#
#
#
# print(f"Считали коды БИН Сбера и исключения, время {int(time.time() - start)}")
#
# # bin_banks_not_sber = ["417367","422838", "431393", "531317", "531344", "533206", "533681", "539013", "545182", "446942", "446915",
# #                       "557029", "557030", "557057", "557071", "557072", "557073", "476208", "676261", "485467", "533616"]
# #
# # bin_banks = ["006", "173", "228", "274", "276", "279", "308", "313", "332", "336", "369", "381", "390", "451", "469", "479",
# #              "484", "570", "762", "817", "854", "0220"]

def convert_data(val):
    return val.date()

def convert_bin(val):
    if type(val) != str:
        return "Другой"
    bin_code = val[0:6]
    sql_str = f"SELECT * FROM bincode WHERE BIN = '{bin_code}';"
    cur.execute(sql_str)
    rezult = cur.fetchall()
    col_name = [el[0] for el in cur.description]
    if len(rezult) == 1:
        rez = dict(zip(col_name,rezult[0]))
        if rez['Банк-эмитент'] != "":
            return rez['Банк-эмитент']
        else:
            return "Другой"
    else:
        return "Другой"


df = pd.read_excel(pd.ExcelFile(filename), "Sheet0")
print(f"чтение файла данных, время {int(time.time() - start)}")


# тут идет проверка бинов в базе
def chk_bank(product):
    if type(product) != str:
        product = "OTHER"
    if "OTHER" in product.upper():
        return "другой"
    else:
        return "Сбербанк"

all_data = df[["Номер карты", "Продукт", "Платежная система"]]
all_data["bincode"] = all_data["Номер карты"].apply(lambda x: x[0:6])
all_data["банк"] = all_data["Продукт"].apply(chk_bank)
all_data_not_sber = all_data[all_data["банк"] != "Сбербанк"]
all_data_not_sber = all_data_not_sber[["bincode", "Платежная система"]]
all_data_not_sber = all_data_not_sber.drop_duplicates(subset=["bincode", "Платежная система"])
all_data_not_sber.sort_values(by=["bincode"], inplace=True)
print(f"получили бинов других банков: {len(all_data_not_sber)}")

all_data = all_data[all_data["банк"] == "Сбербанк"]
all_data = all_data[["bincode", "Платежная система"]]
all_data = all_data.drop_duplicates(subset=["bincode", "Платежная система"])
all_data.sort_values(by=["bincode"], inplace=True)
print(f"получили бинов Сбера: {len(all_data)}")

db = sqlite3.connect("c:\\Vrem\\Python10\\bd_bin_code.db")
cur = db.cursor()


def bin_to_bank(bin_code, plat_syst):
    if type(plat_syst) != str:
        plat_syst = str(plat_syst)
    if plat_syst.upper() == "МИР":
        plat_syst = "Mir"
    sql_str = f"SELECT * FROM bincode WHERE BIN = '{bin_code}';"
    cur.execute(sql_str)
    rezult = cur.fetchall()
    col_name = [el[0] for el in cur.description]
    if len(rezult) == 1:
        rez = dict(zip(col_name,rezult[0]))
        if ("Сбер".upper() in rez['Банк-эмитент'].upper()) and ("росси".upper() in rez['Страна'].upper()):
            if plat_syst.upper() in rez['Платежная система'].upper():
                return "Все совпало"
            else:
                sql_str = f"UPDATE bincode SET 'Платежная система' = '{plat_syst}' WHERE BIN = '{bin_code}';"
                cur.execute(sql_str)
                db.commit()
                # UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
                return f"Бин совпал, система не совпала {rez['Платежная система'].upper()}, система изменена на {plat_syst}"
        else:
            sql_str = f"DELETE FROM bincode WHERE BIN = '{bin_code}';"
            cur.execute(sql_str)
            # db.commit()
            sql_str = f'INSERT INTO bincode ("Банк-эмитент", "Страна", "BIN", "Платежная система") VALUES ("Sberbank, Сбербанк", "Россия", "{bin_code}", "{plat_syst}");'
            cur.execute(sql_str)
            db.commit()
            return f"банк не совпал, в базе был {rez['Банк-эмитент']}, bin переписан на Сбербанк" #изменить все
    elif len(rezult) == 0:
        sql_str = f'INSERT INTO bincode ("Банк-эмитент", "Страна", "BIN", "Платежная система") VALUES ("Sberbank, Сбербанк", "Россия", "{bin_code}", "{plat_syst}");'
        cur.execute(sql_str)
        db.commit()
        return f"не найдено, Bin {bin_code} добавлен"
    else:
        return "странная ситуация"


all_data.reset_index(drop=True, inplace=True)
all_data["Совпадение"] = ""
for i in range(0, len(all_data)):
    if pd.isna(all_data.loc[i, "bincode"]) or pd.isna(all_data.loc[i, "Платежная система"]):
        continue
    all_data.loc[i, "Совпадение"] = bin_to_bank(all_data.loc[i, "bincode"], all_data.loc[i, "Платежная система"])

all_data_not_sber.reset_index(drop=True, inplace=True)
all_data_not_sber["Совпадение"] = ""

count = 1
flag = False
rez = ""
new_bin = 0
for i in range(0, len(all_data_not_sber)):
    procent = int(i / len(all_data_not_sber) * 100)
    if procent >= count:
        if flag:
            print("\b" * len(rez), end="", flush=True)
        rez = f"Обрабатываем операции: {procent}%"
        print(rez, end="")
        count += 1
        flag = True

    if pd.isna(all_data_not_sber.loc[i, "bincode"]):
        continue
    if convert_bin(all_data_not_sber.loc[i, "bincode"]) != "Другой":
        all_data_not_sber.loc[i, "Совпадение"] = f'бин {all_data_not_sber.loc[i, "bincode"]} есть в базе'
        continue
    url = "https://bin-ip-checker.p.rapidapi.com/"
    querystring = {"bin": f"{all_data_not_sber.loc[i, 'bincode']}"}
    payload = {"bin": f"{all_data_not_sber.loc[i, 'bincode']}"}
    headers = {"content-type": "application/json",
               "X-RapidAPI-Key": ,
               "X-RapidAPI-Host": "bin-ip-checker.p.rapidapi.com"}
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    new_bin += 1
    if response.status_code != 404:
        answ_text = response.json()
        if answ_text["success"] and answ_text["code"] == 200:
            if answ_text["BIN"]["valid"] and answ_text["BIN"]["issuer"]["name"] != "":
                platsystem = all_data_not_sber.loc[i, "Платежная система"] if not pd.isna(all_data_not_sber.loc[i, "Платежная система"]) else answ_text["BIN"]["brand"]
                if platsystem.upper() == "МИР":
                    platsystem = "Mir"
                sql_str = f'INSERT OR REPLACE INTO bincode ("BIN", "Платежная система", "Страна", "Банк-эмитент", "Тип карты", "Категория карты", "Адрес сайта банка")' \
                          f' VALUES ("{answ_text["BIN"]["number"]}", "{platsystem}",' \
                          f' "{answ_text["BIN"]["country"]["name"]}", "{answ_text["BIN"]["issuer"]["name"]}",' \
                          f' "{answ_text["BIN"]["type"]}", "{answ_text["BIN"]["level"]}", "{answ_text["BIN"]["issuer"]["website"]}");'
                cur.execute(sql_str)
                db.commit()
                all_data_not_sber.loc[i, "Совпадение"] = f'добавили бин {all_data_not_sber.loc[i, "bincode"]}, банк {answ_text["BIN"]["issuer"]["name"]} система найдена {answ_text["BIN"]["brand"]} система добавлена {platsystem} поиск {new_bin}'
            else:
                all_data_not_sber.loc[i, "Совпадение"] = f'бин {all_data_not_sber.loc[i, "bincode"]} не найден, поиск {new_bin}'
    else:
        all_data_not_sber.loc[i, "Совпадение"] = f'бин {all_data_not_sber.loc[i, "bincode"]} не найден, поиск {new_bin}'

print("\b" * len(rez), end="", flush=True)
print("Обработано 100% операций")

writer = pd.ExcelWriter("chk_bin.xlsx", engine='xlsxwriter')
with writer as file_name:
    all_data.to_excel(file_name, sheet_name="bin_sber", index=False)
    all_data_not_sber.to_excel(file_name, sheet_name="bin_not_sber", index=False)

print(f"Бины проверили {int(time.time() - start)}")

# тут начинается обработка файла данных
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

df["Магазин"] = ""
df["Номер магазина"] = ""
df["QR"] = "эквайринг"
df["проверка комиссии"] = 1
for i in range(0, len(df)):
    tmp_mag = add_magazin(df.loc[i, 'Адрес ТСТ'])
    df.loc[i, 'Магазин'] = tmp_mag[0]
    df.loc[i, 'Номер магазина'] = str(tmp_mag[1])
    if "QR" in df.loc[i, 'Наименование ТСТ']:
        df.loc[i, 'QR'] = "СБП"
    if "ОГНЕВА" in df.loc[i, "Наименование юридического лица"].upper():
        procent = 0.018
    else:
        procent = 0.015
    if df.loc[i, 'QR'] != "СБП":
        df.loc[i, "проверка комиссии"] = abs(round(df.loc[i, "Сумма операции"] * procent - df.loc[i, "Сумма комиссии"]))
    else:
        df.loc[i, "проверка комиссии"] = abs(round(df.loc[i, "Сумма операции"] * procent * 0.8 - df.loc[i, "Сумма комиссии"]))

# # проверяем совпадение кодов сбера и исключений по названиям карт от сбера
# df_chk_bin = df[(df["BIN"] == "Другой") & (~df["Продукт"].str.contains("OTHER", regex=False))]
# df_chk_bin = df_chk_bin[~df_chk_bin['Тип операции'].isin(['Отмена', 'Возврат'])]
# if len(df_chk_bin) > 0:
#     # добавить в bin сбера коды
#     card_numb = df_chk_bin["Номер карты"].tolist()
#     count_new = len(bin_banks)
#     for el in card_numb:
#         if el[0:2] == "22": # проверка карт мир
#             bin_banks.append(el[2:6])
#         else:
#             bin_banks.append(el[1:4])
#     bin_banks = set(bin_banks)
#     bin_banks = list(bin_banks)
#     bin_banks.sort()
#     print(f"Найдено {len(bin_banks)-count_new} новых кодов BIN Сбера")
# else:
#     print("Новых кодов BIN Сбера в таблице не найдено")
#
# df_chk_bin = df[(df["BIN"] == "Сбербанк") & (df["Продукт"].str.contains("OTHER", regex=False))]
# df_chk_bin = df_chk_bin[~df_chk_bin['Тип операции'].isin(['Отмена', 'Возврат'])]
# if len(df_chk_bin) > 0:
#     count_new = len(bin_banks_not_sber)
#     card_numb = df_chk_bin["Номер карты"].tolist()
#     for el in card_numb:
#         bin_banks_not_sber.append(el[0:6])
#     bin_banks_not_sber = set(bin_banks_not_sber)
#     bin_banks_not_sber = list(bin_banks_not_sber)
#     bin_banks_not_sber.sort()
#     print(f"Найдено {len(bin_banks_not_sber)-count_new} новых исключений кодов BIN Сбера")
# else:
#     print("Новых исключений кодов BIN Сбера в таблице не найдено")
#
# print(f"обработали номера карт на предмет карт Сбера, время {int(time.time() - start)}")

banks_data = pd.pivot_table(df,index=['BIN'], values=['Сумма операции'], aggfunc=[sum,len]) # margins=True
banks_data = banks_data.sort_values(by=[('sum','Сумма операции')], ascending=False)
banks_data["% по сумме"] = round(banks_data["sum"]/banks_data["sum"].sum(), 4)
banks_data["% по количеству"] = round(banks_data["len"]/banks_data["len"].sum(), 4)
banks_data.loc['Всего']= banks_data.sum()
banks_data.rename(columns={'sum': 'Сумма операций', 'len': 'Количество операций'}, inplace=True)
cols = list(banks_data.columns.values)
cols = [cols[0], cols[2], cols[1], cols[3]]
banks_data = banks_data[cols]
new_header = [el[0] for el in cols]

print(f"сделали сводную таблицу по банкам, время {int(time.time() - start)}")

mag_komiss = pd.pivot_table(df, index=['Магазин'], columns=["QR"], values=['Сумма комиссии'], aggfunc=sum) # margins=True

print(f"сделали сводную таблицу по комиссиям для Филиппа, время {int(time.time() - start)}")

writer = pd.ExcelWriter("222.xlsx", engine='xlsxwriter')
with writer as file_name:
    df.to_excel(file_name, sheet_name="Sheet0", index=False)
    # banks_data.to_excel(file_name, sheet_name="banks")
    # Convert the dataframe to an XlsxWriter Excel object.
    mag_komiss.to_excel(file_name, sheet_name="Комиссия")
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

# with open("Сбер_data.dat", "w") as file:
#     # запись исключений из сбера, хотя они по бинам подходят и три цифры, начиная со ВТОРОЙ! (для МИР начиная с третьей и 4 цифры) здесь коды сбера
#     file.writelines([str(bin_banks_not_sber)+"\n", str(bin_banks)])
#
# print(f"Записали коды БИН Сбера и исключения, время {int(time.time() - start)}")

db.close()
end = time.time()
print(f"программа выполнена за {int(end - start)} секунд, записан файл 222.xlsx")