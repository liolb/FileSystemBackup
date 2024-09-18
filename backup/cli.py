# command line interface

import argparse
from backup.backupmgr import BackupManager

def main() -> int:
    """Setup and read command line arguments; run the backup manager"""
    # possible args: 
    # define the expected command-line arguments for the program, making it 
    # easier for users to interact with the script.
    # Create an instance of the ⁠ArgumentParser class and assign it to 
    # the variable ⁠parser. This ⁠parser object is what we’ll use to 
    # define and manage the arguments the program accepts.
    # - description: This is a key part of creating a user-friendly CLI. 
    # We provide a brief description of what the script does.  
    # This description will be displayed to the user when they run the 
    # script with the ⁠-h or ⁠--help flag (e.g., ⁠python backup.py -h).
    parser = argparse.ArgumentParser(description='FileSystemBackup: automates file-system backups')
    parser.add_argument('-t', '--dryrun', action='store_true', help='Perform a dry run to test configs and permissions without creating a backup')
    parser.add_argument('-p', '--profile', type=str, default='', help='Id of the profile that should be to back up')
    parser.add_argument('-d', '--destinations', nargs="*", default=[], help='List of destination ids')

    # read argument input
    args = parser.parse_args() 

    # create and run job
    backup_manager = BackupManager(args)
    return backup_manager.run()

