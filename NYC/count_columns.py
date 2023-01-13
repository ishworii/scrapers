import os
import glob
import pandas as pd
from tqdm import tqdm
import json


def count_col(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return len(data.keys())


BASE_DIR = (
    "C:\\Users\\Ishwor\\Desktop\\upwork\\scraping_charles\\data\\1st_batch_100k\\NYC"
)
count = 0
all_folders = os.listdir(BASE_DIR)
for each_folder in tqdm(all_folders):
    # print(each_folder)
    full_path = os.path.abspath(each_folder)
    os.chdir(f"{BASE_DIR}\\{each_folder}")
    json_files = glob.glob("*.json")
    for each_file in json_files:
        col = count_col(each_file)
        count += col
    os.chdir("\\".join(full_path.split("\\")[:-1]))
print(f"Number of columns : {count}")
