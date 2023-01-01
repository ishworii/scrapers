import glob
import os
import zipfile

BASE_DIR = "data"
extension = ".zip"


os.chdir(BASE_DIR)  # change directory from working dir to dir with files

for item in os.listdir():  # loop through items in dir
    if item.endswith(extension):  # check for ".zip" extension
        new_dir = os.path.splitext(item)[0]
        file_name = os.path.abspath(item)  # get full path of files
        try:
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
        except zipfile.BadZipFile:
            pass
        try:
            zip_ref.extractall(f"unzipped_data\\{new_dir}")  # extract file to dir
        except:
            pass
        zip_ref.close()  # close file
        # os.remove(file_name)  # delete zipped file
        # print(file_name)
