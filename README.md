# File System Backup
to help automate file-system backups.

This python script can be used to create compressed backups (`*.zip`) of pre-defined sets of directories or files (wildcards are supported). 
A clean-up mechanism is included as well (all backups older than `today - days_to_keep`are deleted).

In a configuration file (`config.json`) you can declare "backup_profiles" and "backup_destinations".:

**Backup Profiles**
Backup Profiles define file-systems that should be updated. 
You can add as many backup profiles as you wish.

```json
    "backup_profiles": [
        {
            "id": "filesystem_backup_1",         // This is the unique name of the backup profile
            "active": true,                      // Each profile can be set active or inactive
            
            "source": [                          // A file system is defined by a list of search patterns such as
                "*/sample/backup_this_dir/",
                "*/backup_all/*/test_folders/",
                "*/backup_all_textfiles/*.txt"
            ],
            
            "ignore": [                          // Additionally you can exlude files or directories, as for example
                ".*",                            // ignore all files starting with a dot, ...
                "*/not-this-dir/",
                "temp*"
                
            ]
        }   
```
Check [`sample_config.json`](sample_config.json) for some examples.


**Backup Destinations**
Backup Destinations on the other hand define the locations where the backup(s) should be stored. 
(Up to now: only local directories are possible.)

```json
    "backup_destinations": [
        {
            "id": "my_backup_vault",          // This is the unique name of the backup destination
            "active": true,                   // Each destination can be set active or inactive
            "days_to_keep": 28,               // For each destination you can define how long the backup should be stored
                                              // If backups should never be deleted: set `days_to_keep = -1
            "directory": "/destination/"      // directory where the backup should be stored
        }//, ...you can add as many backup destinations as you wish  
```
Check [`sample_config.json`](sample_config.json) for some examples.

## Usage

### 1. Setup the Configuration File
Copy or rename [`sample_config.json`](sample_config.json) to get `config.json`.
Custimize the backup_profile and backup_destination sections to your needs.

### 2. Dry run
Perform a dry run to test the configs. 
Using the command line argument `--dryrun`or `-t` (for "test") you can run the backup process with no backups being created. 

```bash
python3 ./backup.py -t
```

Error logs will be displayed in the terminal if anything in the configration file is wrong. 
The number of files that will be backed up is displayed.

### 3. Run the script 
You can either run the script in its 

- interactive mode (default) or
- specify the backup profile you want to run or
- specify the destination(s) you want the backup to be stored. 

**interactive mode**
If the script is executed without command line argurments

```bash
python3 ./backup.py
```

the backup process runs all active profiles and destinations. I.e.: the file systems of all active profiles will be seperately packed, compressed and backed up to all active destinations. 

Subsequently the clean-up mechanism will be performed in all declared destinations.

**with command line arguments**
- Besides the dry run which runs the backup process without actually creating backups

```bash
// dry run 
python3 ./backup.py --dryrun 

// or
python3 ./backup.py -t
```

- You can define a specific profile you want to run.
  The following example will run only filesystem_backup_1 and create backups on all active destinations

```bash
// define the profile you want to run
python3 ./backup.py -p filesystem_backup_1
```

- You can also target specific destination(s) (one or several).
  The following example will run all active profiles and create backups in my_backup_vault_1 and 2:

```bash
// define the destination(s) that should be used
python3 ./backup.py -d my_backup_vault_1 my_backup_vault_2
```

Backups are created as zip files in the form

	{backup_profile.id}/archive{backup_datetime}.zip
	
## Error alerts

The script has no alert system implemented. 
In case of an error the user will be "notified" by the error log being opened in the standard editor and displayed to the user.