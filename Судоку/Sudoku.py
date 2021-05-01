import tkinter as tk
import pickle as pk
from tkinter import messagebox


class Cell:  # класс для работы непосредственно с данными в клетке

    def __init__(self):
        self.cell = {0: "-", 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}

    def get_cell(self, key):  # ключ для выбора элемента
        return self.cell[key]

    def set_cell(self, key, znac):  # ключ для выбора элемента, знак для присвоения значения
        self.cell[key] = znac


class Pole:

    def __init__(self):
        """ заполняем всю таблицу 9х9. Каждая клетка содержит объект cell со словарем
        где ключ 0 отведен под цифру в клетке, а остальные ключи с 1 по 9 для вариантов возможных цифр"""

        self.all_pole = [[Cell() for i in range(9)] for ii in range(9)]

    def cell_get(self, row, col, digit):  # получить значение из клетки
        return self.all_pole[row][col].get_cell(digit)

    def cell_get_all(self, row, col):
        # получить все варианты значений вариантов из клетки в виде текстовой строки
        # для вывода их на экран, если в клетке еще не стоит цифра
        cell_str = ""
        if str(self.cell_get(row, col, 0)) == "-":
            for digit in range(1, 10):
                if str(self.cell_get(row,col,digit)) == "-":
                    cell_str += "-"
                else:
                    cell_str += str(self.cell_get(row,col,digit))
                if digit == 3 or digit == 6:
                    cell_str += "\n"
                elif digit != 9:
                    cell_str += " "
            return cell_str
        else:
            return str(self.cell_get(row,col, 0))

    def cell_set(self, row, col, digit, znac="-"):
        # записать значение в клетку, если это не нулевое поле, то в вероятные значения цифры
        # записывается прочерк, если ноль, то все вероятные значения обнуляются для этой клетки
        # возвращает False если ошибок нет, либо текстовое сообщение об ошибке (оно же True)
        # if self.cell_check(row, col, znac):
        #     print("можно")
        # else:
        #     print("нельзя")
        if digit == 0:
            if znac != "-":
                if self.cell_get(row, col, znac) == "-":
                    return f"ошибка, в квадрате, ряду или столбце уже есть цифра {znac}\nлибо в клетке нет такого возможного варианта," \
                           f"\nтогда внесите нужный вариант для этой цифры"
                for i in range(1,10):
                    self.all_pole[row][col].set_cell(i, "-")
                self.all_pole[row][col].set_cell(digit, znac)
                self.row_set(row, znac)
                self.col_set(col, znac)
                self.sq_set(row, col, znac)
            else:
                print("ошибка, попытка вставить в финальное значение клетки прочерк. должна быть цифра")
                return "ошибка, попытка вставить в финальное значение клетки прочерк. должна быть цифра"
        else:
            if znac != "-":
                if self.cell_check(row, col, znac):
                    self.all_pole[row][col].set_cell(znac, znac)
                else:
                    print(f"ошибка, в квадрате, ряду или столбце уже есть цифра {znac}")
                    return f"ошибка, в квадрате, ряду или столбце уже есть цифра {znac}"
            else:
                self.all_pole[row][col].set_cell(digit, znac)
        return False

    def cell_check(self, row, col, digit):
        # проверка, можно ли в клетку поставить такую цифру, возвращает истину, если можно
        if digit in self.row_get(row, 0):
            return False
        if digit in self.col_get(col, 0):
            return False
        if digit in self.sq_get(row, col, 0):
            return False
        return True

    def cell_clear(self, row, col):  # очистить одну клетку, путем запоминания значений и обновления (создать заново) все поле
        if self.cell_get(row, col, 0) != "-":
            tmp_pole = []
            for i in range (9):
                tmp_pole.append(self.row_get(i, 0))
            tmp_pole[row][col] = "-"
            self.all_pole = [[Cell() for i in range(9)] for ii in range(9)]
            for i in range(9):  # отправляем цифры в судоку, где они ставятся в поле,а лишние элементы возможных чисел удаляются
                for ii in range(9):
                    if tmp_pole[i][ii] != "-":
                        self.cell_set(i, ii, 0, tmp_pole[i][ii])

    def row_get(self, line, digit):  # получить ряд в виде списка для значений digit
        self.row = []
        for i in range(9):
            self.row.append(self.cell_get(line, i, digit))
        return self.row

    def row_set(self, line, digit):  # записать, точнее стереть цифру и поставить пустое значение во всем ряду в каждую клетку
        for i in range(9):
            self.cell_set(line, i, digit)

    def col_get(self, column, digit): # получить колонку в виде списка для значений digit
        self.kolonka = []
        for i in range(9):
            self.kolonka.append(self.cell_get(i, column, digit))
        return self.kolonka

    def col_set(self, column, digit): # записать, точнее стереть цифру и поставить пустое значение во всей колонке в каждую клетку
        for i in range(9):
            self.cell_set(i, column, digit)

    @staticmethod
    def sq_check(row, col): # определение координат для вывода всех клеток в квадрате
        if 0 <= row < 3:
            row_st = 0
            row_end = 3
        elif 3 <= row < 6:
            row_st = 3
            row_end = 6
        else:
            row_st = 6
            row_end = 9
        if 0 <= col < 3:
            col_st = 0
            col_end = 3
        elif 3 <= col < 6:
            col_st = 3
            col_end = 6
        else:
            col_st = 6
            col_end = 9
        return row_st, row_end, col_st, col_end

    def sq_get(self, row, col, digit):  # получить квадрат по координатам в виде списка для значений digit
        self.sq = []
        row_st, row_end, col_st, col_end = self.sq_check(row,col)
        for i in range (row_st,row_end):
            for ii in range(col_st, col_end):
                self.sq.append(self.cell_get(i, ii, digit))
        return self.sq

    def sq_set(self, row, col, digit):  # получить квадрат по координатам в виде списка для значений digit
        row_st, row_end, col_st, col_end = self.sq_check(row,col)
        for i in range (row_st, row_end):
            for ii in range(col_st,col_end):
                self.cell_set(i, ii, digit)

def reshenie(vse_pole, try_hlp=False):
    """ алгоритм решения поля судоку. На входе переменная, которая должна содержать объект поле
    для расчета, вторая переменная задает режим подсказки или расчета. Можно сюда добавлять и другие алгоритмы
     вычисления в какой клетке будут стоять цифры или где нет вариантов"""

    # сначала проверяем есть ли одиночная возможная цифра в квадрате, если есть, то ее проставляем как конечную
    flag_main = True #Предполагаем что решение есть
    while flag_main: #Цикл по всем вариантам решения цифр в клетках (по квадратам, рядам и т.д.)
        flag_main = False # предполагаем что проход будет один (больше нет решений)
        flag = True
        while flag:
            flag = False
            for digit in range(1,10):
                for i in range(0,7,3):
                    for ii in range(0,7,3):
                        kvadrat = vse_pole.sq_get(i,ii,digit) # получаем данные по цифре и по квадрату
                        if kvadrat.count(digit) == 1: # если в квадрате есть вариант только одной цифры
                            delta_row = kvadrat.index(digit)//3
                            delta_col = kvadrat.index(digit)% 3
                            # print(f"есть {digit} в квадрате {i},{ii} индекс {kvadrat.index(digit)}") # тест
                            # print(f"координата {i+delta_row},{ii+delta_col}") # тест
                            flag = True    # если была найдена цифра, то возможно новое решение, все флаги надо обновить
                            flag_main = True
                            vse_pole.cell_set(i+delta_row, ii+delta_col, 0, digit) # вставляем найденную цифру
                            if try_hlp:
                                lbl_str.set(f"поставлена цифра {digit} в клетку, строка {i+delta_row+1}, столбец {ii+delta_col+1}")
                                pole_button.set(f"{i+delta_row} {ii+delta_col}")
                                return 5
                        elif kvadrat.count(digit) == 2 or kvadrat.count(digit) == 3:  # если в квадрате две или три цифры в ряд или столбец
                            row = []
                            col = []
                            delta_row = 0 # позиция для поиска положения цифры в квадрате, которая запоминается при нахождении нужной позиции
                            delta_col = 0
                            for i_d in range(kvadrat.count(digit)):  # собираем в список координаты клеток для столбцов и колонок
                                row.append(i + kvadrat.index(digit, delta_row) // 3)
                                col.append(ii + kvadrat.index(digit, delta_col) % 3)
                                delta_row = kvadrat.index(digit, delta_row) + 1
                                delta_col = kvadrat.index(digit, delta_col) +1
                            if len(set(row)) == 1 and kvadrat.count(digit) < vse_pole.row_get(row[0], digit).count(digit):  # проверяем все ли координаты равны в ряду (цифры на 1-ой прямой) и есть ли еще комбинации в ряду в других квадратах
                                # print(f"в квадрате есть комбинация цифры {digit} только в ряду {row[0]}")  # тест
                                flag = True  # если была найдена комбинация, то возможно новое решение, все флаги надо обновить
                                flag_main = True
                                for i_d in range(9):  # удаляем из ряда лишние варианты
                                    if i_d not in col and vse_pole.cell_get(row[0], i_d, digit) != "-":  # оставляем саму комбинацию
                                        vse_pole.cell_set(row[0], i_d, digit, "-")
                                if try_hlp:
                                    lbl_str.set(f"в строке {row[0]+1} в одном из квадратов есть линейная комбинация цифры {digit},\n в строке исключены лишние варианты")
                                    return 5
                            if len(set(col)) == 1 and kvadrat.count(digit) < vse_pole.col_get(col[0], digit).count(digit):  # проверяем все ли координаты равны в колонке (цифры на 1-ой прямой) и есть ли еще комбинации в строке в других квадратах
                                # print(f"в квадрате есть комбинация цифры {digit} только в колонке {col[0]}")  # тест
                                flag = True  # если была найдена комбинация, то возможно новое решение, все флаги надо обновить
                                flag_main = True
                                for i_d in range(9):  # удаляем из ряда лишние варианты
                                    if i_d not in row and vse_pole.cell_get(i_d, col[0], digit) != "-":  # оставляем саму комбинацию
                                        vse_pole.cell_set(i_d, col[0], digit, "-")
                                if try_hlp:
                                    lbl_str.set(f"в столбце {col[0]+1} в одном из квадратов есть линейная комбинация цифры {digit},\n в столбце исключены лишние варианты")
                                    return 5

        # проверяем есть ли одиночная возможная цифра в ряду, если есть, то ее проставляем как конечную
        flag = True
        while flag:
            flag = False
            for digit in range(1, 10):
                for i in range(9):
                    row = vse_pole.row_get(i,digit)
                    if row.count(digit) == 1:
                        # print(f"есть {digit} в ряду {i} колонка {row.index(digit)}")  # тест
                        flag = True  # если была найдена цифра, то возможно новое решение, все флаги надо обновить
                        flag_main = True
                        vse_pole.cell_set(i, row.index(digit), 0, digit)  # вставляем найденную цифру
                        if try_hlp:
                            lbl_str.set(f"поставлена цифра {digit} в клетку, строка {i+1}, столбец {row.index(digit)+1}")
                            pole_button.set(f"{i} {row.index(digit)}")
                            return 5

        # проверяем есть ли одиночная возможная цифра в колонке, если есть, то ее проставляем как конечную
        flag = True
        while flag:
            flag = False
            for digit in range(1, 10):
                for i in range(9):
                    col = vse_pole.col_get(i,digit)
                    if col.count(digit) == 1:
                        # print(f"есть {digit} в ряду {col.index(digit)} колонке {i}")  # тест
                        flag = True  # если была найдена цифра, то возможно новое решение, все флаги надо обновить
                        flag_main = True
                        vse_pole.cell_set(col.index(digit), i, 0, digit)  # вставляем найденную цифру
                        if try_hlp:
                            lbl_str.set(f"поставлена цифра {digit} в клетку, строка {col.index(digit)+1}, столбец {i+1}")
                            pole_button.set(f"{col.index(digit)} {i}")
                            return 5

        # проверяем есть ли одиночный вариант возможной цифры в каждой клетке, если есть, то проставляем его как конечную цифру
        flag = True
        while flag:
            flag = False
            for i in range(9):
                for ii in range(9):
                    if vse_pole.cell_get(i, ii, 0) == "-":
                        kletka = []
                        for digit in range(1, 10):
                            if vse_pole.cell_get(i, ii, digit) != "-":
                                kletka.append(vse_pole.cell_get(i, ii, digit))
                        if len(kletka) == 1:
                            # print(f"есть только один вариант цифры {kletka[0]} в ряду {i} колонке {ii}")  # тест
                            flag = True  # если была найдена цифра, то возможно новое решение, все флаги надо обновить
                            flag_main = True
                            vse_pole.cell_set(i, ii, 0, kletka[0])  # вставляем найденную цифру
                            if try_hlp:
                                lbl_str.set(f"поставлена цифра {kletka[0]} в клетку, строка {i+1}, столбец {ii+1}")
                                pole_button.set(f"{i} {ii}")
                                return 5

    # далее проверяем, что произошло после решения
    # подпрограмма возвращает:
    # 1 - если поле полностью решено, возвращается флаг и заполненное поле в виде двумерного списка
    # 2 - не решено, просто кончились варианты в алгоритме решения
    # 3 - не решено, есть клетки без чисел и без вариантов, ошибка схемы, решения нет
    # 4 - подсказок нет, дальше надо что-то самому придумывать
    # 5 - для подсказки выполнено одно действие

    flag_main = 1
    for i in range (9):  # проверка на то, что все цифры заполнены - есть решение
        if "-" in vse_pole.row_get(i, 0):
            flag_main = 2  # если хоть 1 цифры нет
    if flag_main == 1: # все цифры заполнены - есть решение
        return flag_main, [[vse_pole.cell_get(ii, i, 0) for i in range(9)] for ii in range(9)]
    else:  # если решения еще нет
        for i in range(9): # проверка на то, есть ли клетки в котрых нет цифры и нет вариантов, если есть, то схема введена неверно, решения нет
            for j in range(9):
                if str(vse_pole.cell_get(i, j, 0)) == "-":
                    tmp_lst = set({})
                    for digit in range(1, 10):
                        tmp_lst.add(vse_pole.cell_get(i, j, digit))
                    if len(tmp_lst) == 1: # если нет решения задаем флаг и прекращаем подпрограмму
                        flag_main = 3
                        return flag_main
    if try_hlp:
        return 4
    return flag_main

def reshenie_var(vse_pole):
    """ реализован подбор по клеткам, где всего два варианта. Если один вариант из клетки приводит к явной ошибке
     решения, то в клетке стоит второй вариант. Если вариант решился, то судоку решено. Если вариант неявный, то есть
     нет решения и ошибки, то переходим к следующей клетке с с двумя вариантами"""

    # далее идет подбор из вариантов
    rez = 2
    pole_try = [[vse_pole.cell_get(ii, i, 0) for i in range(9)] for ii in range(9)] # получаем текущую схему
    for i in range(9): # ищем клетку с двумя вариантами
        for j in range(9):
            if str(vse_pole.cell_get(i, j, 0)) == "-":
                chk_var = set([vse_pole.cell_get(i, j, d) for d in range(1,10)]) # смотрим сколько вариантов в клетке
                if "-" in chk_var:
                    chk_var.remove("-")
                if len(chk_var) == 2:
                    chk_var = list(chk_var)
                    a = chk_var[0]
                    b = chk_var[1]
                    for p in range(2):
                        if p == 1:
                            chk_var[0] = b
                            chk_var[1] = a
                        pole_try[i][j] = chk_var[0] # ставим вариант в схему
                        sp_var = Pole() # создаем новое поле
                        for d in range(9): #заполняем новое поле на основании схемы с вариантом цифры
                            for dd in range(9):
                                if pole_try[d][dd] != "-":
                                    sp_var.cell_set(d, dd, 0, pole_try[d][dd])
                        rez = reshenie(sp_var) # идем решать на уровень ниже с вариантом в клетке
                        if type(rez) == tuple: # есть решение без ошибки
                            if rez[0] == 1:
                                for d in range(9): # подставляем решение в поле
                                    for dd in range(9):
                                        if vse_pole.cell_get(d, dd, 0) == "-":
                                            vse_pole.cell_set(d, dd, 0, rez[1][d][dd])
                                return rez[0], rez[1]
                        else:
                            if rez == 3: # если подставленная цифра приводит к ошибке
                                vse_pole.cell_set(i, j, 0, chk_var[1]) # если 1 вариант ошибочен то в клетке вторая цифра
                                pole_try[i][j] = chk_var[1]
    return rez

def digit_button_var():  # нажатие кнопок показа вариантов по цифрам
    global dig_bt_var_last # нажатая ранее кнопка
    if str(dig_bt_var.get()) == str(dig_bt_var_last): # если на кнопку нажали второй раз (отмена)
        dig_bt_var.set(0) # присваиваем несуществующее значение
        change_pole()
    else:
        change_pole(dig_bt_var.get())
    dig_bt_var_last = dig_bt_var.get() # запоминаем нажатие

def digit_button():  # нажатие кнопки цифр для ввода цифр

    def put_digit(row, col, dbg): #подпрограмма для вставки цифры в поле
        text_mes = sp.cell_set(row, col, 0, dbg)
        if text_mes:
            lbl_str.set(text_mes)
            change_pole()
        else:
            lbl_str.set(f"Вы поставили цифру {dbg} в клетку {row + 1},{col + 1}\nвнимание! при замене цифры восстанавливаются все варианты")
            if dig_bt_var.get() != 0:
                change_pole(dbg)
            else:
                change_pole()
            file_save(sp)

    if pole_button.get() == "":
        lbl_str.set("Внимание! Для внесения цифры в поле сначала \nнадо выбрать клетку на поле")
        return
    if dig_bt_var.get() != 0 and dig_bt.get() != dig_bt_var.get():
        lbl_str.set(f"Вы можете ставить только цифру {dig_bt_var.get()}\nили снимите показ вариантов нажатием на ту же кнопку {dig_bt_var.get()}")
        return
    row, col = map(int, pole_button.get().split())
    if bt_dgt_var.get() == 0: # если переключатель на цифрах
        if dig_bt_var.get() == 0: # если не показываются варианты
            if knopki[row][col]['text'] != str(dig_bt.get()) and sp.cell_check(row, col, dig_bt.get()): #если нажата не та же цифра, что уже стоит в поле
                if len(knopki[row][col]['text']) == 1: # если уже стоит цифра, сначала очищаем от нее
                    sp.cell_clear(row, col)
                put_digit(row, col, dig_bt.get())
            else:
                lbl_str.set("Эту цифру нельзя сюда поставить")
        else:
            if sp.cell_get(row, col, 0) == "-":
                put_digit(row, col, dig_bt.get())
    else: # тут действия, если работаем с вариантами
        if dig_bt_var.get() == 0: # если не показываются варианты
            if len(knopki[row][col]['text']) == 1: # если уже стоит цифра то вариант вставить нельзя
                lbl_str.set("В клетке уже стоит цифра,\nпоэтому вариант невозможно сюда поставить")
                return
            else:
                if sp.cell_get(row, col, dig_bt.get()) == "-": # если надо вернуть цифру вместо прочерка
                    sp.cell_set(row, col, dig_bt.get(), dig_bt.get())
                    lbl_str.set(f"Вы поставили вариант цифры {dig_bt.get()} в клетку {row + 1},{col + 1}")
                else: # если убираем подсказку (замена цифры на прочерк)
                    var_check = set([sp.cell_get(row, col, i) for i in range(1,10)])
                    if len(var_check) == 2 and dig_bt.get() in var_check:
                        lbl_str.set("В клетке не может вообще не остаться вариантов,\nклетка без вариантов и цифры является ошибочным решением")
                        return
                    sp.cell_set(row, col, dig_bt.get(), "-")
                    lbl_str.set(f"Вы убрали вариант цифры {dig_bt.get()} из клетки {row + 1},{col + 1}")
                change_pole()
                file_save(sp)
    flag = True
    for i in range (9):  # проверка на то, что все цифры заполнены - есть решение
        if "-" in sp.row_get(i, 0):
            flag = False  # если хоть 1 цифры нет
    if flag: # все цифры заполнены - есть решение
        lbl_str.set("СУДОКУ РЕШЕНО!")
    # dig_bt.set(0) # не будет видно нажатия

def change_pole(*args): # печатает значения и варианты во всем поле ячеек
    flag = False # предполагаем, что в клетке варианты, а не число
    for i in range(9):
        for j in range(9):
            if len(args) == 0: # если агументов нет собираем весь набор - 9 элементов
                tmp_str = sp.cell_get_all(i, j)
            else: # если аргументы есть, получаем 1 знак
                if sp.cell_get(i, j, 0) == args[0]: # проверяем в клетке число или вариант числа
                    tmp_str = str(args[0])
                    flag = True
                else:
                    tmp_str = str(sp.cell_get(i, j, args[0]))
            if knopki[i][j]['text'] != tmp_str or flag:
                if (len(tmp_str) == 1 and len(args) == 0) or flag:
                    knopki[i][j]['font'] = font_big
                    knopki[i][j]['text'] = tmp_str
                else:
                    knopki[i][j]['font'] = font_small
                    knopki[i][j]['text'] = tmp_str
            flag = False


def digit_button_can(): # отмена ввода числа в ячейку
    if pole_button.get() == "":
        lbl_str.set("Внимание! Для удаления цифры из поля сначала \nнадо выбрать клетку на поле")
        return
    row, col = map(int, pole_button.get().split())
    if sp.cell_get(row, col, 0) == "-":
        lbl_str.set(f"в клетке с координатой {row + 1},{col + 1} и так нет никакой цифры")
    elif dig_bt_var.get() != 0 and knopki[row][col]['text'] == "-":
        lbl_str.set(
            f"Вы можете очистить только цифру {dig_bt_var.get()}\nили снимите показ вариантов нажатием на ту же кнопку {dig_bt_var.get()}")
        return
    else:
        sp.cell_clear(row, col)
        lbl_str.set(f"Вы очистили клетку с координатой {row + 1},{col + 1}\nвнимание! при сбросе цифры восстанавливаются все варианты")
        if dig_bt_var.get() != 0:
            knopki[row][col]['font'] = font_small
            change_pole(dig_bt_var.get())
        else:
            change_pole()
        file_save(sp)

def digit_button_hlp():  # нажатие на кнопку подсказки
    digit_button_ras(True)

def digit_button_cls(): # нажатие на кнопку очистить все поле
    if dig_bt_var.get() == 0: # если не показываются варианты
        sp.__init__()
        change_pole()
        file_save(sp)
        lbl_str.set("Внесите исходную схему судоку, которую надо решить\n поставив цифры в соответствующие поля")
    else:
        lbl_str.set("Сначала отмените режим показа вариантов цифры")


def digit_button_ras(hlp=False):  #нажатие на кнопку расчета, если аргумент истина то это нажата кнопка помощи
    if dig_bt_var.get() == 0: # если не показываются варианты
        rez = reshenie(sp, hlp)
        if type(rez) == tuple:
            rez = rez[0]
        if rez == 2 and not hlp:
            rez = reshenie_var(sp)
            if type(rez) == tuple:
                rez = rez[0]
        if rez == 1:
            lbl_str.set("СУДОКУ РЕШЕНО!")
        elif rez == 2:
            lbl_str.set("пытались решить, но решение не найдено")
        elif rez == 3:
            lbl_str.set("не решено, есть клетки без вариантов, ошибка схемы, решения нет")
        elif rez ==4:
            lbl_str.set("подсказок нет и окончательное решение пока не найдено")
        change_pole()
        file_save(sp)
    else:
        lbl_str.set("Сначала отмените режим показа вариантов цифры")

def file_save(sud_pole, name = 1):  #запись основного поля в файл, арумент - экземпляр поля судоку
    if name == 1:
        fn = "sudoku.dat"
    else:
        fn = f"sudokuv{name - 1}.dat"

    with open(fn, "wb") as file:
        pk.dump(sud_pole, file, pk.HIGHEST_PROTOCOL)

def file_open(name):
    try:  #попытка открыть файл с ранее сохраненной схемой судоку, если есть сохранение, то из него, если нет, то результат ЛОЖЬ
        file = open(name, mode ='rb')
        sp = pk.load(file)
        file.close()
    except FileNotFoundError:
        sp = Pole() # если файла нет то делаем пустое поле
    finally:
        file_save(sp) # записываем загруженное поле
    return sp

def buttons_file(): #нажатие на кнопки запоминания и загрузки файлов варианта 1
    buttons_file_all(1, dig_bt_file_one.get())
    dig_bt_file_one.set(2)

def buttons_file_two(): #нажатие на кнопки запоминания, загрузки и удаления файлов варианта 2
    buttons_file_all(2, dig_bt_file_two.get())
    dig_bt_file_two.set(2)

def buttons_file_tre(): #нажатие на кнопки запоминания, загрузки и удаления файлов варианта 3
    buttons_file_all(3, dig_bt_file_tre.get())
    dig_bt_file_tre.set(2)

def buttons_file_all(var, knopka): #нажатие на кнопки запоминания, загрузки и удаления файлов
    global sp
    if knopka == 0:
        file_save(sp, var + 1)
        messagebox.showinfo("Сохранение", f"поле клеток сохранено в варианте {var}")
    elif knopka == 1:
        if messagebox.askyesno(f"загрузка сохранения {var}",
                               "Вы действительно хотите восстановить ранее сохраненный вариант?"):
            sp = file_open(f"sudokuv{var}.dat")
            if dig_bt_var.get() != 0:
                change_pole(dig_bt_var.get())
            else:
                change_pole()

def press_key(event_full):
    if event_full.keysym.isdigit():
        key_dig = int(event_full.keysym)
        if 1 <= key_dig <= 9:
            dig_bt.set(key_dig)
            digit_button()
    else:
        key_dig = event_full.keysym
        if key_dig == "Escape":
            digit_button_can()
        if key_dig in ("Left", "Up", "Down", "Right"):
            if pole_button.get() == "":
                row = col = 0
            else:
                row, col = map(int, pole_button.get().split())
                if key_dig == "Up":
                    row -= 1
                elif key_dig == "Down":
                    row += 1
                elif key_dig == "Left":
                    col -= 1
                elif key_dig == "Right":
                    col += 1
                if row > 8:
                    row = 8
                elif row < 0:
                    row = 0
                if col > 8:
                    col = 8
                elif col < 0:
                    col = 0
            pole_button.set(f"{row} {col}")

# тут начало программы (после всех определений подпрограмм и классов)
count_level = 0 # временная для понимания уровня рекурсии
dig_bt_var_last = "" #для запоминания последней нажатой клавиши вариантов

win = tk.Tk() #создаем основное окно и задаем все начальные параметры
win.title("Помощник для решения Sudoku")
high = 600
wide = 700
starthigh = 100
startwide = 100
back_ground_color = "#a39e9e"
font_small = ("TkDefaultFont",9)
font_big = ("TkDefaultFont",20)
win.geometry(f"{wide}x{high}+{startwide}+{starthigh}")

win.resizable(True, True)
win.minsize(wide, high)
win.maxsize(wide+600, high+300)
photo = tk.PhotoImage(file="icon.png") #Sud3.png table.png
win.iconphoto(False, photo)
win.config(bg=back_ground_color)  #a39e9e, #757373

for i in range(13):
    win.columnconfigure(i, minsize=50, weight=1)
for i in range(12):
    win.rowconfigure(i, minsize=50, weight=1)
win.bind("<Key>", press_key)

# начинаем заполнять поле кнопок и расчетное поле со значениями из файла или создавая пустое поле
# создаем ракмки
ramka = [[0] for i in range(13)]
for i in range(13):
    ramka[i] = tk.Frame(win, relief=tk.RIDGE, borderwidth=5)
ramka[0].grid(row=0, column=0, columnspan=3, rowspan=3, stick="nesw") # рамки для поля цифр
ramka[1].grid(row=0, column=3, columnspan=3, rowspan=3, stick="nesw")
ramka[2].grid(row=0, column=6, columnspan=3, rowspan=3, stick="nesw")
ramka[3].grid(row=3, column=0, columnspan=3, rowspan=3, stick="nesw")
ramka[4].grid(row=3, column=3, columnspan=3, rowspan=3, stick="nesw")
ramka[5].grid(row=3, column=6, columnspan=3, rowspan=3, stick="nesw")
ramka[6].grid(row=6, column=0, columnspan=3, rowspan=3, stick="nesw")
ramka[7].grid(row=6, column=3, columnspan=3, rowspan=3, stick="nesw")
ramka[8].grid(row=6, column=6, columnspan=3, rowspan=3, stick="nesw")

ramka[9].grid(row=11, column=0, columnspan=3, stick="nesw") # рамки для работы с файлами
ramka[10].grid(row=11, column=3, columnspan=3, stick="nesw")
ramka[11].grid(row=11, column=6, columnspan=3, stick="nesw")
ramka[12].grid(row=11, column=11, columnspan=2, stick="nesw")
# конфигурация одной двенадцатой рамки
ramka[12].rowconfigure(1, minsize=20, weight=1)
ramka[12].rowconfigure(2, minsize=20, weight=1)
ramka[12].columnconfigure(0, minsize=55, weight=1)
# конфигурация рамок для файлов
for i in range(9):
    for j in range(3):
        ramka[i].columnconfigure(j, minsize=45, weight=1)
        ramka[i].rowconfigure(j, minsize=45, weight=1)
for i in range(9,12):
    ramka[i].rowconfigure(1, minsize=10, weight=1)
    ramka[i].rowconfigure(2, minsize=30, weight=1)
    for j in range(2):
        ramka[i].columnconfigure(j, minsize=45, weight=1)


knopki = [[0]*9 for i in range(9)]  # создаем двумерный список для поля кнопок
txt_pole = ""
# sp = Pole() # создаем поле цифр
lbl_str = tk.StringVar()
sp = file_open("sudoku.dat") # попытка открыть файл с ранее сохраненной схемой судоку, если есть сохранение, то из него, если нет, то новое поле
lbl_str.set("Если хотите очистить поле и начать заново, нажмите кнопку"
            "\n'Очистить все поле'. Схему судоку можно решить, поставив"
            "\nцифры в соответствующие поля. Цифры судоку ставятся с помощью"
            "\nцифровых кнопок справа из первого ряда, второй ряд управляет"
            "\nпоказом вариантов по отдельной цифре")
pole_button = tk.StringVar()
for f in range(9):
    for ii in range(3):
        for jj in range(3):
            if f == 0:
                i = ii
                j = jj
            elif f == 1:
                i = ii
                j = jj + 3
            elif f == 2:
                i = ii
                j = jj + 6
            elif f == 3:
                i = ii + 3
                j = jj
            elif f == 4:
                i = ii + 3
                j = jj + 3
            elif f == 5:
                i = ii + 3
                j = jj + 6
            elif f == 6:
                i = ii + 6
                j = jj
            elif f == 7:
                i = ii + 6
                j = jj + 3
            elif f == 8:
                i = ii+ 6
                j = jj+ 6
            knopki[i][j] = tk.Radiobutton(ramka[f], text="", font=font_small, indicatoron=0, selectcolor="yellow", variable=pole_button, value=f"{i} {j}") #1 2 3\n4 5 6\n7 8 9
            knopki[i][j].grid(row=ii, column=jj, stick="nesw")

change_pole()

dig_bt = tk.IntVar()
dig_bt_var = tk.IntVar()
dig_bt_file_one = tk.IntVar()
dig_bt_file_one.set(2)
dig_bt_file_two = tk.IntVar()
dig_bt_file_two.set(2)
dig_bt_file_tre = tk.IntVar()
dig_bt_file_tre.set(2)
for i in range(1, 10):
    tk.Radiobutton(win, text=i, command=digit_button, font=font_big, variable=dig_bt, value=i, indicatoron=0).grid(row=i-1, column=10, stick="nesw")
    tk.Radiobutton(win, text=i, command=digit_button_var, font=font_big, variable=dig_bt_var, value=i, indicatoron=0).grid(row=i-1, column=12, stick="nesw")

photo_save = tk.PhotoImage(file="save.png")
photo_load = tk.PhotoImage(file="load.png")
lbl_file_one = tk.Label(ramka[9], text="память один", font=("TkDefaultFont",8)).grid(row=1, column=0, columnspan=3, stick="nesw")
lbl_file_two = tk.Label(ramka[10], text="память два", font=("TkDefaultFont",8)).grid(row=1, column=0, columnspan=3, stick="nesw")
lbl_file_tre = tk.Label(ramka[11], text="память три", font=("TkDefaultFont",8)).grid(row=1, column=0, columnspan=3, stick="nesw")
button_file = [[] for i in range(2)]
for i in range(2):
    button_file[i] = tk.Radiobutton(ramka[9], text="F1", image=photo_save, command=buttons_file, font=font_small, indicatoron=0, selectcolor="yellow",
                     variable=dig_bt_file_one, value=i)
    button_file[i].grid(column=i, row=2, stick="nesw")
button_file[1].config(image=photo_load )
button_file_two = [[] for i in range(2)]
for i in range(2):
    button_file_two[i] = tk.Radiobutton(ramka[10], text="F2", image=photo_save, command=buttons_file_two, font=font_small, indicatoron=0, selectcolor="yellow",
                     variable=dig_bt_file_two, value=i)
    button_file_two[i].grid(column=i, row=2, stick="nesw")
button_file_two[1].config(image=photo_load )
button_file_tre = [[] for i in range(2)]
for i in range(2):
    button_file_tre[i] = tk.Radiobutton(ramka[11], text="F3", image=photo_save, command=buttons_file_tre, font=font_small, indicatoron=0, selectcolor="yellow",
                     variable=dig_bt_file_tre, value=i)
    button_file_tre[i].grid(column=i, row=2, stick="nesw")
button_file_tre[1].config(image=photo_load )

btn_can = tk.Button(win, text="Сброс цифры", command=digit_button_can, font=font_small).grid(row=9, column=9, columnspan=2, stick="nesw")
btn_hlp = tk.Button(win, text="Подсказка", command=digit_button_hlp, font=font_small).grid(row=10, column=9, columnspan=2, stick="nesw")
btn_ras = tk.Button(win, text="Решить", command=digit_button_ras, font=font_small).grid(row=11, column=9, columnspan=2, stick="nesw")
btn_cle = tk.Button(ramka[12], text="Новое поле", command=digit_button_cls, font=("TkDefaultFont",8)).grid(row=1, column=0, stick="nesw")
btn_var = tk.Button(ramka[12], text="Пересчет вар.", command=digit_button_cls, font=("TkDefaultFont",8)).grid(row=2, column=0, stick="nesw")

lbl_pole = tk.Label(win, textvariable=lbl_str, font=font_small, bg="#e8e9ff").grid(row=9, column=0, columnspan=9, rowspan=2, stick="nesw")
lbl_btn = tk.Label(win, text="-->\n|\n|\n|\n|\n|\n|\n|\n\nЦифры\n\nдля\n\nввода\n\nв\n\nполе\n\n|\n|\n|\n|\n|\n|\n|\n-->", font=font_small, bg=back_ground_color).grid(row=0, column=9, rowspan=9, stick="nesw")
lbl_btn1 = tk.Label(win, text="-->\n|\n|\n|\n|\n|\n|\n|\n\nНажми\nЦифру\nдля\nпоказа\nполя\nтолько\nпо\nней\n\nповтор\nцифры\n-\nотмена\n\n|\n|\n|\n-->", font=font_small, bg=back_ground_color).grid(row=0, column=11, rowspan=9, stick="nesw")

bt_dgt_var = tk.IntVar()
bt_dgt_var.set(0)
tk.Radiobutton(win, text="Цифры", font=font_small, variable=bt_dgt_var, value=0, indicatoron=0, selectcolor="yellow").grid(row=9, column=11, columnspan=2, stick="nesw")
tk.Radiobutton(win, text="Варианты", font=font_small, variable=bt_dgt_var, value=1, indicatoron=0, selectcolor="yellow").grid(row=10, column=11, columnspan=2, stick="nesw")

win.mainloop()

