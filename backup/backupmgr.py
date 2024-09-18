import os
import shutil
import datetime
import tempfile
import typing
import argparse

from .configs import ConfigObject, Profile, Destination
from .logmgr import LogManager
from .utils import filter_files, create_zip, copy_file, open_with_editor


class BackupManager():

    def __init__(self, args: typing.Union[argparse.Namespace, dict]):
        # accept input
        self.args = args

        # create backup-datetime stamp as an ident for the backup run
        self.backup_time: str = datetime.datetime.now().strftime("%y%m%d%H%M%S")

        # setup log
        self.log = LogManager(self.backup_time)

        # load configurations (from config.json file)
        self.config_filepath: str = os.path.join(os.path.dirname(__file__), 'config.json') 
        if not os.path.isfile(self.config_filepath):
            raise Exception('Config file not found. Please ensure that the file is present:\n{}'.format(self.config_filepath))
        self.configs = ConfigObject(self.config_filepath, self.log)


    def _do_backup(self, profiles: list[Profile], destinations: list[Destination]) -> None:
        if (len(profiles) == 0) or (len(destinations) == 0):
            self.log.log_hint('Backup process completed. No valid and active profiles or destinations defined.\n')
            return

        for profile in profiles:
            self.log.log_hint('\n[{}]:: Start backup of file system (profile: "{}")'.format(profile.id, profile.id))
            self.log.log_hint('[{}]:: Collecting files...'.format(profile.id))

            files = filter_files(profile.source, profile.ignore)

            self.log.log_hint('[{}]:: Found {} files to back up.'.format(profile.id, len(files)))
            if len(files) == 0: 
                self.log.log_hint('[{}]:: Please check the configuration file {}'.format(profile.id, self.config_filepath))
                return
            
            if not self.args.dryrun:
                # we create a compressed archive of the file system in a temporary dictionary
                self.log.log_hint('[{}]:: Creating backup...'.format(profile.id))
                temp_dir = tempfile.mkdtemp()
                try: 
                    backup_file = create_zip(files, temp_dir)

                    self.log.log_hint('[{}]:: Copying backup to {} backup destinations...'.format(profile.id, len(destinations)))
                    destination_foldername = 'BACKUP_{}'.format(profile.id)
                    for destination in destinations:
                        destination_path = os.path.join(destination.directory, destination_foldername)
                        copy_file(backup_file, destination_path)  
                        self.log.log_hint('[{}]:: File system backed up to:\n{}\n'.format(profile.id, destination_path + '/' + os.path.basename(backup_file)))

                finally:
                    #remove artifacts
                    if temp_dir and os.path.isdir(temp_dir):
                        shutil.rmtree(temp_dir)
            else:
                self.log.log_hint('Dry run. No backup is created.')            

        self.log.log_hint('Backup process completed!\n')


    def _do_cleanupMechanism(self, destinations: list[Destination]) -> None:
        from .utils import cleanup_destination
        for destination in destinations:
            cleanup_destination(destination.directory, destination.days_to_keep)              


    def _getBackupProfiles(self) -> list[Profile]:
        profiles: list[Profile] = []
        if (self.args.profile is not None) and (self.args.profile != ''):
            # user wants to backup the file system of only one specific profile
            try:
               profile = self.configs.profiles.get(self.args.profile.strip())
               profiles.append(profile)
            except:
               self.log.log_error('Profile "{}" does not exist in config file {}'.format(self.args.profile, self.config_filepath)) 
               return 1  
        else:
            # no restrictions made by user; we backup all active profiles
            profiles = [profile for profile in list(self.configs.profiles.values()) if profile.active == True]    

        return profiles


    def _getBackupDestinations(self) -> list[Destination]:
        backup_destinations: list[Destination] = []
        if (self.args.destinations is not None) and (len(self.args.destinations) > 0):
            for destination_id in self.args.destinations:
                try:
                    destination = self.configs.destinations.get(destination_id.strip())
                    backup_destinations.append(destination)
                except:
                    self.log.log_error('Destination "{}" does not exist in config file {}'.format(destination, self.config_filepath)) 
        else:
            # no restrictions made by user; we backup to all active destinations
            backup_destinations = [destination for destination in list(self.configs.destinations.values()) if destination.active == True]         
        
        return backup_destinations


    def run(self) -> int:  
        """Main method - use this to get the job done"""
        if self.args.dryrun:
            self.log.log_hint('\nSTART Dry run backup process.\n')
        else:
            self.log.log_hint('\nSTART Backup process\n')
        
        backup_profiles = self._getBackupProfiles()  
        backup_destinations = self._getBackupDestinations()
        self._do_backup(backup_profiles, backup_destinations)

        if not self.args.dryrun:
            all_destinations: list[Destination] = list(self.configs.destinations.values())
            self._do_cleanupMechanism(all_destinations)

        # How to notify the user, that an error occured? #Krücke:
        open_with_editor(self.log.get_errorlog_file())    

        return 0    