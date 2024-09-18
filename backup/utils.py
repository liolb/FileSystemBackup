import os
import shutil
import glob
import fnmatch
from datetime import datetime
import tarfile
import zipfile
import csv
import json

BACKUP_DIR_PREFIX = 'BACKUP_'
BACKUP_FILENAME_PREFIX = 'archive'
BACKUP_FILENAME_FORMAT_DATETIMESTAMP = '%Y%m%d%H%M%S'


def readJson(filepath: str) -> dict:
    try:
        if os.path.exists(filepath):
            # with open(): ensures that the file is automatically closed when 
            # we are done with it, even if an error occurs during processing.
            with open(filepath, 'r') as json_file:
            #with open(file_path, "r", encoding="utf-8", errors="surrogateescape") as json_file:
                data = json.load(json_file)
            return data
        return {}
    except PermissionError:
        raise Exception('Permission denied for reading: {}'.format(filepath))
    except json.JSONDecodeError as e:
        raise Exception('Invalid JSON format: {}'.format(filepath))


def filter_files(file_patterns: list[str], ignore_patterns: list[str] = []) -> list[str]:
    # This method returns a list of all files matchting any of the file_patterns,
    # excluding those matching any of the ignore patterns.
    # 
    # Args:
    #     file_patterns (list): A list of directory paths and/or files to search. 
    #     ignore_patterns (list): A list of glob patterns to ignore. 
    #
    #     where both args support wildcards:
    #     ⁠"*"  : matches any characters, 
    #     "⁠?"  : matches any single character, 
    #     "[]" : matches any character within the specified range (e.g., ⁠[a-z], ⁠[0-9], ⁠[A-Za-z]).
    #
    # Returns:
    #    A list of file paths matching any of the file_patterns, but none of the ignore_patterns.
    #
    # Example usage:
    #    file_patterns = ["/path/to/directory1", "/path/to/directory2",‚ "/path/to/**/subdir/"]
    #    ignore_patterns = ["*.txt", "temp*", "**/logs/*"]  
    #    filtered_files = filter_files(file_patterns, ignore_patterns) 
    #
    # where
    #    "*.txt": Matches any file ending with “.txt”.
    #    "temp*"": Matches any file starting with “temp”.
    #    ""⁠**/logs/*": Matches any file within a directory named “logs” at any level of the directory tree.  
     
    if file_patterns == None:
        return []
    
    filtered_files: list[str] = [] 
    for file_pattern in file_patterns:
        # using glob.glob(): glob.glob() can be used as a wildcard search (search w/ *, ? or []) for files. 
        # within the file system. It returns a list of all file paths that match the provided directory file pattern
        for file in glob.glob(file_pattern, recursive=True):
            if os.path.isdir(file):
                # handling directores
                for root, _, files in os.walk(file):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # using ⁠fnmatch.fnmatch to check if the current ⁠file matches any of the ⁠ignore_patterns.
                        # ⁠fnmatch.fnmatch supports wildcards like ⁠* (match any characters) and ⁠? (match any single character).
                        if any(fnmatch.fnmatch(full_path, pattern) for pattern in ignore_patterns):
                            continue  # skip this file if it matches an ignore pattern
                        filtered_files.append(full_path)
            else:
                # handling files 
                files = glob.glob(file)
                for file in files:
                    if any(fnmatch.fnmatch(file, pattern) for pattern in ignore_patterns):
                        continue
                    filtered_files.append(file) 

    # remove duplicates from list
    unique_result = set()
    for file in filtered_files:
        unique_result.add(file)
    filtered_files = list(unique_result)  

    return filtered_files


def create_tar_gz(filepaths: list[str], destination_directory: str) -> str:
    # cd to destination dir; save orig.
    saved_path: str = os.getcwd()
    os.chdir(destination_directory)
    try:
        timestamp = datetime.now().strftime(BACKUP_FILENAME_FORMAT_DATETIMESTAMP)
        backup_file = "archive{}.tar.gz".format(timestamp)

        with tarfile.open(backup_file, "w:gz") as tar:
            for filepath in filepaths:
                tar.add(filepath, arcname=filepath)
        tar.close()
    finally:
        os.chdir(saved_path)
   
    return os.path.join(destination_directory, backup_file)


def create_zip(filepaths: list[str], destination_directory: str) -> str:
    # cd to destination dir; save orig.
    saved_path: str = os.getcwd()
    os.chdir(destination_directory)
    try:
        timestamp = datetime.now().strftime(BACKUP_FILENAME_FORMAT_DATETIMESTAMP)
        backup_file = "archive{}.zip".format(timestamp)

        with zipfile.ZipFile(backup_file , "w") as zip:
            for filepath in filepaths:
               zip.write(filepath, filepath)
    finally:
        os.chdir(saved_path)

    return os.path.join(destination_directory, backup_file)    


def cleanup_destination(destination_directory: str, days_to_keep: int) -> None:
    if days_to_keep < 1:
        return

    saved_path: str = os.getcwd()
    os.chdir(destination_directory)
    try:
        now = datetime.now()
        for root, dirs, files in os.walk(destination_directory):
            for dir in dirs:
                if not dir.startswith(BACKUP_DIR_PREFIX):
                    dirs.remove(dir)
            for file in files:
                if file.startswith(BACKUP_FILENAME_PREFIX):
                    file_datetime = datetime.strptime(file[len(BACKUP_FILENAME_PREFIX):-4], BACKUP_FILENAME_FORMAT_DATETIMESTAMP)
                    difference = now - file_datetime
                    if difference.days > days_to_keep:
                        full_path = os.path.join(root, file)
                        os.remove(full_path)
            #if not glob.glob(os.path.join(root, '*')): #os.listdir(root):
             #   os.remove(root)


    finally:
        os.chdir(saved_path)

   

def copy_file(file: str, destination_dir: str):
    if not os.path.exists(file):
        return False
    
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    target_file = os.path.join(destination_dir, os.path.basename(file))
    try:
        shutil.copy(file, target_file)
        return True
    except PermissionError as e:
        raise PermissionError(f"Permission error during copy: {e}")
    except OSError as e:
        raise OSError(f"Error during file copy: {e}")
    

def writeCsv(filepath: str, data: list) -> None:
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    if os.path.isfile(filepath) and not os.access(filepath, os.W_OK):
        filepath = filepath[:-4] + "-1.log"
    try:
        
        with open(filepath, "a", newline="", encoding="utf-8", errors="backslashreplace") as f:
            writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)
    except Exception:
        filepath = filepath[:-4] + "-1.log"
        with open(filepath, "a", newline="", encoding="utf-8", errors="backslashreplace") as f:
            writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)  


def open_with_editor(file_path):
    import platform
    
    if platform.system() == 'Darwin':  # macOS
        os.system(f"open {file_path}")
    elif platform.system() == 'Windows':
        os.system(f"start notepad.exe {file_path}") 
    else:
        print("Unsupported operating system.")                