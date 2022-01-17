import pylightxl as xl
import os
import pyodbc
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
import win32com.client as win32
from shutil import rmtree
from time import sleep

# ежемесячно задаем начальные параметры для работы
# подпрограммы для диалогового окна и собственно окно для определения переменных
# year_now - нужный год, по которому выбираются отгрузки
# subdir - подкаталог, где лежат файлы и одновременно месяц года
# flag_chk_invoice - проверка на что делаем, ложь - распределение счетов в базе, истина - обработка складских файлов
subdir = None
year_now = None
flag_chk_invoice = True

# функция для сравнения строковых переменных, делает все большие и убирает пробелы и слеши из строки
name = lambda n: n.upper().replace(" ","").replace("/","").replace("Ё","Е")

# очистка директории, если в ней что-то остается, возникает сбой при попытке конвертировать файлы в 127 строке программы
f_loc = r'C:\Users\micrab\AppData\Local\Temp\gen_py'
all_dir = os.listdir(f_loc)
if len(all_dir) != 0:
    for f in all_dir:
        if os.path.isfile(f_loc+chr(92)+f):
            os.remove(f_loc+chr(92)+f)
        else:
            rmtree(f_loc+chr(92)+f)

# открываем доступ к базе данных, считывание данных
fn = "D:\\Работа\\baza\\kosmbase.mdb"
conn_str = "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)}; DBQ=" + fn +";"
cnxn = pyodbc.connect(conn_str)
crsr = cnxn.cursor()

# подпрограмма для распределения отгрузок по счетам в базе
def account_to_deliv(mnts, yrnow):
    # проверяем наличие счетов и их распределение
    sql = f"""SELECT Document.dkompany, Document.Numdoc, Document.datadoc, Document.sumdoc, Document.zachto, Document.doccomment, Del_prs.Доставка, Del_prs.Допрасходы, Del_prs.Итого, [sumdoc]-[Итого] AS Проверка
    FROM Document LEFT JOIN Del_prs ON Document.Numdoc = Del_prs.paper
    WHERE (((Month([datadoc]))={mnts}) AND ((Document.Vid)=1) AND ((Document.PodVid)=2) AND ((Year([datadoc]))={yrnow}))
    ORDER BY Document.dkompany, Document.datadoc;"""
    crsr.execute(sql)
    tb = pd.DataFrame(list(map(list, crsr.fetchall())), columns=[name[0] for name in crsr.description])
    if len(tb) == 0:
        print("Счета в этом месяце не выставляли")
        crsr.close()
        cnxn.close()
        exit(0)
    if len(tb[tb['Проверка'].notna()]) == len(tb):
        print("Все счета в этом месяце уже распределены")
        if len(tb[tb['Проверка'].astype('int32') == 0]) != len(tb):
            print("Но есть расхождения счетов и поставок")
            print(tb[tb['Проверка'].astype('int32') != 0].to_string())
        crsr.close()
        cnxn.close()
        exit(0)
    elif len(tb[tb['Проверка'].isna()]) != 0:  # если найдены нераспределенные счета
        tb = tb[tb["Проверка"].isna()] # далее создаем две колонки месяца и даты из поля "зачто" счетов
        col_mont = []
        col_year = []
        for el in tb['zachto']:
            el = el.replace(" ", "")
            try:
                el = tuple(map(int, el[len(el) - 7:].split(".")))
                if el[0] not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12) or not (2019 <= el[1] <= 2030):
                    raise ValueError
            except ValueError:
                el = [None, None]
            col_year.append(el[1])
            col_mont.append(el[0])
        # tb["mes"] = col_mont # добавляем колонки в датафрейм
        tb.loc[:, 'mes'] = col_mont
        # tb["yer"] = col_year
        tb.loc[:, 'yer'] = col_year
        count = len(tb)
        el = []
        for index, row in tb.iterrows(): # перебираем счета по строкам
            sql = f"""SELECT Year([date_magasin]) AS Год, Month([date_magasin]) AS Месяц, TrPrice.kod_org, TrPrice.paper, TrPrice.Sklad, Sum(TrPrice.price_delivery) AS car, Sum(TrPrice.price_add) AS car_add, Sum(TrPrice.CarPrice) AS itog
            FROM TrPrice GROUP BY Year([date_magasin]), Month([date_magasin]), TrPrice.kod_org, TrPrice.paper, TrPrice.Sklad
            HAVING (((Year([date_magasin]))={row['yer']}) AND ((Month([date_magasin]))={row['mes']}) AND ((TrPrice.kod_org)={row['dkompany']}));"""
            crsr.execute(sql) # создаем таблицу отгрузок по году, месяцу и компании для сверки их сумм со счетами
            tb_del = pd.DataFrame(list(map(list, crsr.fetchall())), columns=[name[0] for name in crsr.description])
            if len(tb_del) != 1:
                # tb_tmp = tb_del[tb_del['itog'].astype('int32') == int(row['sumdoc'])].reset_index(drop=True) # ищем совпадения по сумме
                tb_tmp = tb_del[abs(tb_del.itog - int(row['sumdoc'])) <= 3].reset_index(drop=True)
            elif len(tb_del) == 1:
                tb_tmp = tb_del
            if len(tb_tmp) == 0:
                tb_tmp = tb_del[tb_del['paper'].isna()].reset_index(drop=True)  # если строчек несколько и сумма не совпала берем только где нет счетов
            if len(tb_tmp) == 1: # если все совпало будет одна строчка, тогда надо внести номера счетов в отгрузки и склад в счета
                sql = f"""UPDATE TrPrice SET paper ='{row['Numdoc']}' WHERE (((Year([date_magasin]))={row['yer']}) AND ((Month([date_magasin]))={row['mes']}) AND ((TrPrice.kod_org)={row['dkompany']})
                AND ((TrPrice.Sklad)='{tb_tmp.at[0, 'Sklad']}') AND ((TrPrice.paper) Is Null));"""
                crsr.execute(sql)
                cnxn.commit()
                sql = f"""UPDATE Document SET doccomment = ('{tb_tmp.at[0, 'Sklad']}' & ' ' & doccomment) 
                WHERE(((Document.dkompany)={row['dkompany']}) AND((Document.Numdoc) = '{row['Numdoc']}') AND((Document.Vid) = 1) AND((Document.PodVid) = 2));"""
                crsr.execute(sql)
                cnxn.commit()
                el.append(f"Cчет {row['Numdoc']} привязан к отгрузкам\n")
            else: # скорее всего суммы не совпали и счетов было несколько
                el.append(f"Cчет {row['Numdoc']} не распределен\n")
                print(f"Cчет {row['Numdoc']} не распределен")
            count -= 1
            print(f"Cчет {row['Numdoc']} обработан, осталось {count} счетов")
    with open("report.txt", "w", encoding = "UTF-8") as file_to:
        print(*el, file=file_to)
    # Завершаем подключение.
    crsr.close()
    cnxn.close()
    exit(0)

# подпрограмма обработка нажатия на кнопку обработки файлов или распределения счетов
def digit_button_ent():
    global subdir, year_now, flag_chk_invoice
    all_dir = os.listdir(combo_month.get())
    files = [combo_month.get()+chr(92)+f for f in all_dir if os.path.isfile(combo_month.get()+chr(92)+f)]
    subdir = combo_month.get()
    # 1. проверить каталог на наличие файлов
    if flag_chk_invoice: # Если это нажатие на кнопку обработки файлов, а не распределения счетов
        if len(files) == 0:
            messagebox.showerror("В каталоге нет файлов.", "Проверьте каталог или выберите другой")
            return
        # 2. проверить есть ли в каталоге старые файлы
        for file_name in files:
            if ".xlsx" not in file_name:
                # если есть старые файлы, они конвертируются в новые, путем обращения непосредственно к Excel
                # модуль import win32com.client as win32
                fname = os.getcwd() + chr(92) + file_name
                # с помощью кода ниже можно обойти ошибку, возникающую при запуске екселя
                # ошибка связана с указанной системной директорией, из которой надо все удалить
                try:
                    excel = win32.gencache.EnsureDispatch('Excel.Application')
                except AttributeError:
                    ## excel.Application.Quit()
                    # f_loc = r'C:\Users\micrab\AppData\Local\Temp\gen_py'
                    # all_dir = os.listdir(f_loc)
                    # if len(all_dir) != 0:
                    #     for f in all_dir:
                    #         if os.path.isfile(f_loc+chr(92)+f):
                    #             os.remove(f_loc+chr(92)+f)
                    #         else:
                    #             rmtree(f_loc+chr(92)+f)
                    #     sleep(5)
                    #     excel = win32.gencache.EnsureDispatch('Excel.Application')
                    print("очисть вручную каталог " + r"C:\Users\micrab\AppData\Local\Temp\gen_py")
                wb = excel.Workbooks.Open(fname)
                fname = fname.lower() + "x"
                wb.SaveAs(fname, FileFormat=51)  # FileFormat = 51 is for .xlsx extension
                wb.Close()                       # FileFormat = 56 is for .xls extension
                excel.Application.Quit()
                os.remove(file_name)
                sleep(3)
                print(f"Найдены старые файлы. Файл '{file_name}' конвертирован в последний формат .xlsx")
    # 3. проверить правильность ввода года
    if year_pole.get().isdigit():
        if int(year_pole.get()) in range(2019,2030):
            year_now = int(year_pole.get())
        else:
            err = "Ошибка ввода года", "Год должен быть между 2019 и 2030"
            if flag_chk_invoice:
                messagebox.showerror(err)
                return
            else:
                raise ValueError(err)
    else:
        err = "Ошибка ввода года", "Год должен состоять из цифр"
        if flag_chk_invoice:
            messagebox.showerror(err)
            return
        else:
            raise ValueError(err)
    # 4. закрыть окно и продолжить программу
    win.destroy()

def digit_button_account():
    global subdir, year_now, flag_chk_invoice
    flag_chk_invoice = False
    digit_button_ent()
    # try:
    account_to_deliv(subdir, year_now)
    # except:
    #     win.destroy()
    #     crsr.close()  # завершаем подключение к базе данных Access
    #     cnxn.close()
    #     exit(0)


def digit_button_can():
    win.destroy()
    crsr.close()  # завершаем подключение к базе данных Access
    cnxn.close()
    exit(0)

def on_closing():
    crsr.close()  # завершаем подключение к базе данных Access
    cnxn.close()
    win.destroy()
    exit(0)

win = tk.Tk() #создаем основное окно и задаем все начальные параметры
win.title("Работа со складом")
high = 250
wide = 300
starthigh = 200
startwide = 200
back_ground_color = "#e8e9ff" #"#a39e9e"
font_small = ("TkDefaultFont",9)
font_big = ("TkDefaultFont",20)
win.geometry(f"{wide}x{high}+{startwide}+{starthigh}")
win.resizable(False, False)
win.minsize(wide, high)
# win.maxsize(wide+600, high+300)
win.config(bg=back_ground_color)  #a39e9e, #757373
win.protocol("WM_DELETE_WINDOW", on_closing)

tk.Label(win, text="Надо выбрать месяц (каталог с файлами)", font=font_small, bg="#e8e9ff", anchor="center").pack()
dirs = [f for f in os.listdir() if os.path.isdir(f) and f.isdigit()]
dirs = [f for f in dirs if 0 < int(f) < 13]
combo_month = ttk.Combobox(win, values = dirs, state = "readonly")
combo_month.pack()
combo_month.current(dirs.index(max(dirs)))
tk.Label(win, text="и ввести год (по умолчанию текущий)", font=font_small, bg="#e8e9ff", anchor="center").pack()
year_now = datetime.date.today().year
y_n = tk.IntVar()
y_n.set(year_now)
year_pole = tk.Entry(win, textvariable = y_n)
year_pole.pack()
tk.Label(win, text="Обработать файлы склада и \nвнести их в базу", font=font_small, bg="#e8e9ff", anchor="center").pack()
tk.Button(win, text="Обработать файлы", command=digit_button_ent, font=font_small).pack()
tk.Label(win, text="Распределить счета по отгрузкам в базе\n месяц применяется к дате счетов", font=font_small, bg="#e8e9ff", anchor="center").pack()
tk.Button(win, text="Распределить счета", command=digit_button_account, font=font_small).pack()
tk.Button(win, text="Отмена", command=digit_button_can, font=font_small).pack()
win.mainloop()
# конец обработки ввода года и каталога с файлами для месяца

# класс для работы с таблицами
class Table:
    """работа с таблицами. Принимаем, что первая (нулевая) строка это заголовки,
     и данные начинаются с 1 строки и с 1 колонки, то есть первая клетка имеет координаты 1,1"""

    def __init__(self, table):
        self.table = table  # таблица это двумерный список, где каждый элемент это строка,
        # а кадлый элемент в строке, это данные по калонке
        self.col_col = len(self.table[0])  # количество колонок
        self.col_row = len(self.table)  # количество строк включая строку заголовка
        for i in range(self.col_row):  # проверка, что каждая строка имеет оинаковое количество элементов
            if len(self.table[i]) != self.col_col:
                err = f"ошибка формирования таблицы, нарушена целостность данных. В строке {i} не хватает данных \n{self.table[i]}"
                raise ValueError(err)

    def __str__(self):
        return str(self.table)

    def all_table(self):  # возвращает всю таблицу
        return self.table

    def check_col(self, col):
        # проверка номера колонки, подразумевается, что первая колонка начинается с 1 (реально с 0)
        # и преобразование имени колонки в индекс колонки
        if isinstance(col, int):
            col = col - 1
        elif isinstance(col, str):
            if col not in self.table[0]:
                err = f"ошибка. нет такого имени в заголовках {col}"
                raise ValueError(err)
            col = self.table[0].index(col)
        else:
            err = f"ошибка. что-то не так с номером колонки {col}"
            raise ValueError(err)
        if col < 0 or col > self.col_col:
            err = f"ошибка. неправильный номер колонки {col}"
            raise ValueError(err)
        return col  # выдает реальный индекс для списка, отсчет с нуля

    def check_row(self, row):
        # у строк нет смещения, так как данные начинаются с 1 строки
        if not isinstance(row, int):
            err = f"ошибка. что-то не так с номером строки {row}"
            raise ValueError(err)
        if row < 0 or row >= self.col_row:
            err = f"ошибка. неправильный номер строки {row}"
            raise ValueError(err)
        return row

    def cell(self, *arg):
        # получение данных из клетки (2 аргумента) или запись значения в клетку (3 аргумента)
        # координаты должны быть "табличные" то есть первая клетка 1,1
        if len(arg) >= 2:
            row = self.check_row(arg[0])
            col = self.check_col(arg[1])
        else:
            err = f"ошибка. слишком мало арументов {arg}"
            raise ValueError(err)
        if len(arg) == 2:
            return self.table[row][col]
        elif len(arg) == 3:
            self.table[row][col] = arg[2]
        else:
            err = f"ошибка. слишком много арументов {arg}"
            raise ValueError(err)

    def add_col(self, name, vol = ""): # добавление колонки с пустыми или заданными значениями
        self.table[0].append(name)
        self.col_col = len(self.table[0])
        for i in range(1, self.col_row):
            self.table[i].append(vol)

    def del_col(self, col): # удаление колонки по номеру или имени
        col = self.check_col(col)
        for i in range(self.col_row):
            del self.table[i][col]
        self.col_col = len(self.table[0])

    def get_col(self, col):
        # получение данных колонки в виде одномерного списка данных, не забываем, что запрос начинается с 1 (первая колонка)
        col = self.check_col(col)
        col_list = []
        for i in range(1, self.col_row):
            col_list.append(self.table[i][col])
        return col_list

    def get_row(self, row):
        # получение данных строчки в виде одномерного списка данных, не забываем, что запрос начинается с 1 (первая колонка)
        row = self.check_row(row)
        row_list = []
        for i in range(self.col_col):
            row_list.append(self.table[row][i])
        return row_list

    def del_row(self, row): # удаление строки по номеру
        row = self.check_row(row)
        del self.table[row]
        self.col_row = len(self.table)


# задаем начальные параметры для работы
# Список колонок, который должен быть в таблице
col_name = ['Дата загрузки', 'Дата выгрузки', 'Гос. № а/м и п/прицепа   ( Забор)', 'Адрес погрузки',
            '№ магазина', 'Полное наименование', 'Адрес выгрузки ', 'ФИО водителя',
            'Гос. № а/м и п/прицепа ( доставка )', 'Кол-во паллет', 'Стоимость доставки за паллет с НДС ',
            'Доп.расходы.   (перегруз,перевес,  простой, разгрузка) с НДС', 'Всего']
# переименование колонок
col_name_new = ['Дата загрузки', 'Дата выгрузки', 'Номер машины загрузка', 'Адрес погрузки',
                'Название магазина', 'Организация', 'Адрес выгрузки', 'Водитель',
                'Номер машины доставка', 'Паллет', 'Доставка',
                'Доп.расходы', 'Всего']
# ненужные колонки
no_col = ['Дата загрузки', 'Номер машины загрузка', 'Адрес погрузки', 'Адрес выгрузки']

# название складов
sklad = ['Гермес', 'Маклайн', 'Тракт']
clear_tabl = [] #для всей таблицы данных считываемой из файлов
key_table = '№ п/п' #ключ для клетки с которой начинается прямоугольник таблицы
skl = "" #для определения имени склада
strt_time = datetime.date(1900, 1, 1) # объект для конвертации даты

# конвертация даты из строки в число в формат для Excel
def str_to_data(ds): # предполагается, что формат даты д-м-г если ошибка то берет г-м-d
    global strt_time
    if isinstance(ds, int):
        return ds
    else:
        if ds == "":
            return ""
        d = ""
        dd = []
        for i in ds:
            if i.isdigit():
                d += i
            else:
                dd.append(int(d))
                d = ""
        dd.append(int(d))
        try:
            return (datetime.date(dd[2] if dd[2]>100 else dd[2]+2000, dd[1], dd[0]) - strt_time).days + 2
        except ValueError:
            return (datetime.date(dd[0] if dd[0]>100 else dd[0]+2000, dd[1], dd[2]) - strt_time).days + 2

# проврка значения и конвертация в целое
def str_to_int(ds):
    if isinstance(ds, int):
        return ds
    else:
        if ds == "":
            return 0
        elif ds.isdigit():
            return int(ds)
        else:
            err = "ошибка. попытка конвертировать строки в число"
            raise ValueError(err)

def poisk(a, b, c=0): # поиск элемента в списке и возврат номера строки, если найден и 0 если не найден
    # a - список где ищем , b -что ищем, с - позиция с которой ищем, по умолчанию с 0
    try:
        c = a.index(b, c)
    except ValueError:
        c = -1
    return c

# создаем список файлов с данными в указанном подкаталоге
all_dir = os.listdir(subdir)
files = [subdir+chr(92)+f for f in all_dir if os.path.isfile(subdir+chr(92)+f)]
# перебираем по файлам, беря только с именами складов
for file_name in files:
    for i in sklad:
        if name(i) in name(file_name):
            # readxl returns a pylightxl database that holds all worksheets and its data
            db = xl.readxl(fn=file_name)
            sheets = db.ws_names # получаем список имен листов в файле, если их несколько
            for sheet in sheets:
                if name("партнеры") in name(sheet): # имя листа должно содержать слово "партнеры"
                    # db.ws(sheet).set_emptycell(val="")
                    # request a semi-structured data (ssd) output
                    # Предполагается, что таблица на листе будет только одна (начинающаяся с заданного ключа)
                    ssd = db.ws(sheet).ssd(keycols=key_table, keyrows=key_table)
                    if ssd != []:
                        # Проверка целостности данных
                        if len(ssd[0]['keycols']) == len(col_name[0]): # проверка количества колонок
                            if name(ssd[0]['keycols'][0]) == name("Дата"): ssd[0]['keycols'][0] = 'Дата загрузки'
                            for i in range(len(ssd[0]['keycols'])): #проверка на совпадение и порядок колонок
                                if name(ssd[0]['keycols'][i]) != name(col_name[i]):
                                    err = f"ошибка. в файле '{file_name}' нарушен порядок строк на листе '{sheet}' \nили имена не совпадают должна быть колонка '{ssd[0]['keycols'][i]}' а в файле '{col_name[i]}'"
                                    raise ValueError(err)
                        else:
                            err = f"ошибка. несовпадение количества колонок в файле '{file_name}'"
                            raise ValueError(err)
                        # собираем таблицу из заголовка и данных построчно
                        if len(clear_tabl) == 0: # если это начало работы, то надо добавить первую строчку с названием столбцов
                            clear_tabl.append(col_name_new)
                            clear_tabl[0].append("Склад")
                        # тут добавляем строчки данных и склад в таблицу
                        for i in sklad: # перебираем склады по именам
                            if name(i) in name(file_name): skl = i # если имя входит в имя файла, запоминаем имя файла
                        for row in ssd[0]['data']:
                            row.append(skl)
                            clear_tabl.append(row)
                    else:
                        print(f'в файле "{file_name}" в листе "{sheet}" таблица не найдена')
data_sklad = Table(clear_tabl)

# Получаем данные по магазинам из базы
sql = "SELECT Magazin.magkey, Magazin.magname, Magazin.nomer FROM Magazin WHERE (((Magazin.Неработает)=False));"
names=['magkey', 'magname', 'nomer']
crsr.execute(sql)
result = crsr.fetchall()
i = 0
for el in result:
    result[i] = list(el)
    i += 1
result.insert(0, names)
# создаем таблицу (экземпляр) магазинов
magazins = Table(result)
# Получаем данные по оргазациям
sql = "SELECT Kompanii.orgkey, Kompanii.Namesm FROM Kompanii WHERE (((Kompanii.Sobstv)=True) AND ((Kompanii.neaktivna)=False));"
names=['orgkey', 'Namesm']
crsr.execute(sql)
result = crsr.fetchall()
i = 0
for el in result:
    result[i] = list(el)
    i += 1
result.insert(0, names)
# создаем таблицу (экземпляр) организаций
kompanii = Table(result)
# Получаем данные по поставкам
sql = f"""SELECT Document.datadoc, Document.dmagazin, Document.dkompany, Document.dockey, Document.doccomment, Document.zachto
FROM Document WHERE (((Year([datadoc]))={year_now}) AND ((Month([datadoc]))={subdir}) AND ((Document.Vid)=1)
AND ((Document.PodVid) Is Null Or (Document.PodVid)=17)) ORDER BY Document.datadoc DESC;"""
names=["datadoc", "dmagazin", "dkompany", "dockey", "doccomment", "zachto"]
crsr.execute(sql)
result = crsr.fetchall()
i = 0
for el in result:
    result[i] = list(el)
    i += 1
result.insert(0, names)
# создаем таблицу (экземпляр) поставок
delivery = Table(result)
delivery.add_col("pmag", 0)
# приводим дату к формату электронных таблиц
for i in range(1, delivery.col_row):
    delivery.cell(i, "datadoc", str_to_data(delivery.cell(i,"datadoc").strftime("%d.%m.%Y")))
    try:
        delivery.cell(i,"pmag", int(delivery.cell(i,"doccomment").split()[-2]))
    except:
        pass
# добавляем колонку для проверки использования записи при привязки кодов отгрузки к складским отгрузкам
delivery.add_col("use", False)
# получаем данные по уже имеющимся отгрузкам в таблице стоимости транспорта для проверки при добавлении данных в базу
sql = "SELECT TrPrice.KeyDoc FROM TrPrice ORDER BY TrPrice.KeyDoc DESC;"
crsr.execute(sql)
# тут нужен только список, поэтому алгоритм несколько другой
result = crsr.fetchall()
i = 0
for el in result:
    result[i] = el[0]
    i += 1

# начинаем обрабатывать данные
# удалить лишние колонки
for i in no_col:
    data_sklad.del_col(i)
# добавить нужные колонки с пустыми значениями в данные со складов
new_col = ["Номер магазина","Номер Счета", "Код маг", "Код орг", "Проверка", "Код отгрузки", "Паллет в магазине", "Контроль паллет"]
for i in new_col:
    data_sklad.add_col(i)
# получаем все номера наших магазинов
mag_list = magazins.get_col('nomer')
for i in range(len(mag_list)):
    mag_list[i] = str(mag_list[i])
    mag_list[i] = "0" * (4 - len(mag_list[i])) + mag_list[i]
# получаем список наших организаций, предварительно взяв 1 слово из названия
org_list = kompanii.get_col('Namesm')
for i in range(len(org_list)):
    b = org_list[i].find(" ")
    if b != -1:
        org_list[i] = org_list[i][:b]

# проходим по всему списку строк поставок по колонке магазин и проверяя в них наличие нашего магазина
# если магазин не наш строка удаляется,
# если наш, данные в строке проверяются, добавляются или конвертируются
mag_list_data = data_sklad.get_col("Название магазина")
for i in range(len(mag_list_data), 0,-1):
    flag = -1 # не наш магазин
    for j in range(len(mag_list)):
        if mag_list[j] in mag_list_data[i-1]:
            flag = j
            break
    if flag != -1: # если магазин наш, заполняем таблицу правильными данными сверяя их с базой
        data_sklad.cell(i,"Номер магазина", str_to_int(mag_list[flag]))
        data_sklad.cell(i,"Код маг", str_to_int(magazins.cell(flag+1,'magkey')))
        data_sklad.cell(i, "Название магазина", magazins.cell(flag+1,'magname'))
        data_sklad.cell(i, "Номер машины доставка", name(data_sklad.cell(i,"Номер машины доставка")))
        data_sklad.cell(i, "Дата выгрузки", str_to_data(data_sklad.cell(i, "Дата выгрузки")))
        data_sklad.cell(i, "Паллет", str_to_int(data_sklad.cell(i, "Паллет")))
        data_sklad.cell(i, "Доставка", str_to_int(data_sklad.cell(i, "Доставка")))
        data_sklad.cell(i, "Доп.расходы", str_to_int(data_sklad.cell(i, "Доп.расходы")))
        data_sklad.cell(i, "Всего", str_to_int(data_sklad.cell(i, "Всего")))
        data_sklad.cell(i, "Проверка", data_sklad.cell(i, "Всего") - data_sklad.cell(i, "Доставка") - data_sklad.cell(i, "Доп.расходы"))
        for j in range(len(org_list)):
            if org_list[j] in data_sklad.cell(i, "Организация"):
                data_sklad.cell(i, "Организация", org_list[j])
                data_sklad.cell(i, "Код орг", int(kompanii.cell(j+1, "orgkey")))
        # начинаем сопоставление отгрузок от склада с данными по отгрузкам из базы
        pos_elem = 0 # две технические переменные для поиска даты отгрузки
        flag_dva = 0
        tmp_list = delivery.get_col("datadoc")
        # Дата отгрузки по складу может отличаться от даты отгрузки по документу на один день, поэтому дату ищем тройным
        # проходом сравнивая сегодня, вчера и завтра с данными из базы
        while pos_elem <= len(tmp_list):
            if flag_dva == 0:
                pos_elem = poisk(tmp_list, data_sklad.cell(i, "Дата выгрузки"), pos_elem)
                if pos_elem == -1:
                    pos_elem = 0
                    flag_dva = 1
            if pos_elem == -1 or flag_dva == 1:
                pos_elem = poisk(tmp_list, data_sklad.cell(i, "Дата выгрузки") - 1, pos_elem)
                if pos_elem == -1:
                    pos_elem = 0
                    flag_dva = 2
            if pos_elem == -1 or flag_dva == 2:
                pos_elem = poisk(tmp_list, data_sklad.cell(i, "Дата выгрузки") + 1, pos_elem)
                if pos_elem == -1:
                    data_sklad.cell(i, "Код отгрузки", 0)
                    break
            # если дата нашлась, проверям остальные поля и вносим данные, если поля соответствуют отгрузке
            # за счет поля use запись отгрузки можно использовать только один раз
            if data_sklad.cell(i, "Код маг") == delivery.cell(pos_elem + 1, "dmagazin") \
                    and 'подарочные карты'.upper() not in delivery.cell(pos_elem + 1, "zachto").upper() \
                    and not delivery.cell(pos_elem + 1, "use"):
                data_sklad.cell(i,"Код отгрузки", delivery.cell(pos_elem + 1, "dockey"))
                data_sklad.cell(i, "Паллет в магазине", delivery.cell(pos_elem + 1, "pmag"))
                data_sklad.cell(i, "Контроль паллет", data_sklad.cell(i, "Паллет") - data_sklad.cell(i, "Паллет в магазине"))
                delivery.cell(pos_elem + 1, "use", True)
                break
            else:
                pos_elem += 1
    else:
        data_sklad.del_row(i)
# запись полученной таблицы данных в файл для проверки
td = data_sklad.all_table()
sheet = "alldata"
fn = f"all_month_{subdir}_2021.xlxs"
# add a blank worksheet to the db
# create a black db
db = xl.Database()
db.add_ws(sheet)
for i in range(len(td)):
    for j in range(len(td[0])):
        db.ws(sheet).update_index(i+1, j+1, val=td[i][j])
# # write out the db
xl.writexl(db, fn)

#запись данных в базу
count = 0
for i in range(1, data_sklad.col_row):
    if data_sklad.cell(i,'Код отгрузки') and data_sklad.cell(i,'Код отгрузки') not in result:
        # paper не вводим = Номер Счета
        sql = """INSERT INTO TrPrice (KeyDoc, CarPrice, Sklad, date_magasin, Driver, car_number, pallet, price_delivery, price_add, kod_mag, kod_org)
        VALUES ({}, {}, '{}', '{}', '{}', '{}', {}, {}, {}, {}, {});""".format(data_sklad.cell(i, 'Код отгрузки'), data_sklad.cell(i, 'Всего'),
                data_sklad.cell(i, 'Склад'), datetime.timedelta(days=(data_sklad.cell(i,'Дата выгрузки') - 2)) + strt_time,
                data_sklad.cell(i, 'Водитель'), data_sklad.cell(i, 'Номер машины доставка'), data_sklad.cell(i, 'Паллет'),
                data_sklad.cell(i, 'Доставка'), data_sklad.cell(i, 'Доп.расходы'), data_sklad.cell(i, 'Код маг'),
                data_sklad.cell(i, 'Код орг'))
        crsr.execute(sql)
        count += 1

cnxn.commit() # сохраняем изменения в базе
crsr.close() # завершаем подключение к базе данных Access
cnxn.close()

print(f"Обработано {data_sklad.col_row-1} записей, из них добавлено в базу {count}")
win = tk.Tk()
win.withdraw()
messagebox.showinfo("обработка закончена успешно", f"Обработано {data_sklad.col_row-1} записей, из них добавлено в базу {count}")