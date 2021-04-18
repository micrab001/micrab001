import os
import os.path

# C:\\Users\\micrab C:\\Vrem\\PHYTHON
subdir = "C:\\Vrem\\PHYTHON"
subdir = os.path.normcase(subdir)

print(subdir)

print(os.path.getatime(subdir)) # последний доступ
print(os.path.getmtime(subdir)) # последние изменения
print(os.path.getctime(subdir)) # время создания
print(os.path.getsize(subdir)) # размер


all_dir = os.listdir(subdir)
# files = [subdir+chr(92)+f for f in all_dir if os.path.isfile(subdir+chr(92)+f)]
# dirs = [subdir+chr(92)+f for f in all_dir if os.path.isdir(subdir+chr(92)+f)]
files = [f for f in all_dir if os.path.isfile(subdir+chr(92)+f)]
dirs = [f for f in all_dir if os.path.isdir(subdir+chr(92)+f)]



print(all_dir)
print(files)
print(dirs)
