# (python3) generate_dataset.py --class={class} --directories={dir1,dir2} --copy_or_move=0/1

import numpy as np

import argparse
import os
import random
import shutil
from sys import platform


parser = argparse.ArgumentParser(description="Script para generar datasets de clasificacion de imagenes...")

required_group = parser.add_argument_group(title='required arguments')
required_group.add_argument("-c", "--clas", type=str, required=True, help="nombre de la clase para introducir en el dataset")
required_group.add_argument("-d", "--directories", type=str, required=True, help="rutas de carpetas con las imagenes, definir separados por comas: path/num/1,path/num/2")
parser.add_argument("-m", "--copy_or_move", type=int, default=0, choices= [0, 1], help="0 para copiar las fotos, 1 para moverlas")
args = parser.parse_args()

args.directories = args.directories.split(",")


flag_folders_bien = True
for folder in args.directories:
    if not os.path.isdir(folder):
        flag_folders_bien = False
        print(f"[ERROR] - '{folder}' no es una carpeta")
print("[INFO] - rutas de directorios confirmadas")

if not flag_folders_bien:
    print("\nSaliendo del programa...")
    exit(1)

padding = 7
phase_folders = ["train", "val", "test"]

for phase_name in phase_folders:
    if not os.path.isdir(phase_name):
        os.mkdir(phase_name)
    if not os.path.isdir(os.path.join(phase_name, args.clas)):
        os.mkdir(os.path.join(phase_name, args.clas))
print("[INFO] - carpetas de etapas y clase creadas")

####################################
# --> se necesita un labels.txt??? #
####################################

for folder in args.directories:

    files = []
    for f in os.listdir(folder):
        if os.path.isfile(os.path.join(".", folder, f)):
            files.append(os.path.join(".", folder, f))
    print(f"[INFO] - {folder} - obtenidos los ficheros de la carpeta '{folder}'")

    files_70 = random.sample(files, int(len(files) * 0.7))
    # print(files_70)
    # print(len(files_70))
    _files_30 = list(set(files) - set(files_70))
    # print(_files_30)
    # print(len(_files_30))
    files_20 = random.sample(_files_30, int(len(_files_30) * 0.67))
    # print(files_20)
    # print(len(files_20))
    files_10 = list(set(_files_30) - set(files_20))
    # print(files_10)
    # print(len(files_10))
    print(f"[INFO] - {folder} - reparto de imagenes para el dataset realizado")

    files_list = [files_70, files_20, files_10]
    counter_train = len(os.listdir(os.path.join(phase_folders[0], args.clas))) + 1
    counter_val = len(os.listdir(os.path.join(phase_folders[1], args.clas)) )+ 1
    counter_test = len(os.listdir(os.path.join(phase_folders[2], args.clas))) + 1

    for folder_files_couple in zip(phase_folders, files_list):
        for f in folder_files_couple[1]:
            join_list = [".", folder_files_couple[0], args.clas]
            if platform == "win32":
                join_list.append(str(f).split("\\")[-1].split(".")[-1])
            else:
                join_list.append(str(f).split("/")[-1].split(".")[-1])
            if folder_files_couple[0] == "train":
                join_list[-1] = f"{str(counter_train).zfill(padding)}." + join_list[-1]
                counter_train += 1
            elif folder_files_couple[0] == "val":
                join_list[-1] = f"{str(counter_val).zfill(padding)}." + join_list[-1]
                counter_val += 1
            elif folder_files_couple[0] == "test":
                join_list[-1] = f"{str(counter_test).zfill(padding)}." + join_list[-1]
                counter_test += 1
            # print(f)
            # print(os.path.join(*join_list))
            if args.copy_or_move == 0:
                shutil.copy2(f, os.path.join(*join_list))
            elif args.copy_or_move == 1:
                os.rename(f, os.path.join(*join_list))

    print(f"[INFO] - {folder} - dataset creado con exito")
