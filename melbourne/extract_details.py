import os
import glob
import pandas as pd
from tqdm import tqdm
import csv


def count_col_rows(filename):
    with open(filename) as file:
        try:
            first_line = file.readline()
            rows = file.readlines()
        except:
            rows = []
            first_line = ""
    ncols = len(first_line.split(","))
    nrows = len(rows)
    if nrows > 200:
        return ncols, nrows
    return 0, 0


BASE_DIR = "data\\unzipped_data"
count = 0
all_folders = os.listdir(BASE_DIR)
total_cols = 0
total_rows = 0
count_csv_files = 0
for each_folder in tqdm(all_folders):
    # print(each_folder)
    full_path = os.path.abspath(each_folder)
    os.chdir(f"{BASE_DIR}\\{each_folder}")
    csv_files = glob.glob("*.csv")
    count_csv_files += len(csv_files)
    for each_file in csv_files:
        col, rows = count_col_rows(each_file)
        if col != 0:
            count += 1
        total_cols += col
        total_rows += rows
    os.chdir("\\".join(full_path.split("\\")[:-1]))
print(f"Number of cols : {total_cols}")
print(f"Number of rows : {total_rows}")
print(f"Number of csv files : {count_csv_files}")
print(f"Number of valid files : {count}")
