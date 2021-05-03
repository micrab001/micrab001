import pandas as pd
import time

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

df = pd.read_excel(pd.ExcelFile("111.xlsx"), "Sheet0")
for col in df.columns:
    if col not in ['Дата операции', 'Дата выгрузки в АБС', 'Сумма операции',
       'Сумма комиссии', 'Сумма расчета']:
        df[col] = df[col].astype("str")
        df[col] = df[col].apply(lambda x: "" if x == "nan" else x )
df.insert(df.columns.get_loc('Дата операции')+1,'Дата операции магазин', df["Дата операции"].apply(convert_data))
df.insert(df.columns.get_loc('Продукт')+1,'BIN', df["Номер карты"].apply(convert_bin))
df.to_excel("222.xlsx", sheet_name="Sheet0", index=False)

end = time.time()
print(f"программа выполнена за {int(end - start)} секунд")