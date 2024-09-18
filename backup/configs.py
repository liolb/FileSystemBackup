from .logmgr import LogManager

BACKUP_PROFILES = 'backup_profiles'
BACKUP_DESTINATINS = 'backup_destinations'
PROFILE_IDENT  = 'id'
PROFILE_ACTIVE = 'active'
PROFILE_SOURCE = 'source'
PROFILE_IGNORE = 'ignore'
DESTINATION_IDENT = 'id'
DESTINATION_ACTIVE = 'active'
DESTINATION_DIRECTORY = 'directory'
DESTINATION_DAYS_TO_KEEP = 'days_to_keep'


class Profile:
    
    def __init__(self):
        self.active: bool = False
        self.id: str = ''
        self.source: list[str] = []
        self.ignore: list[str] = []

    def is_valid(self, log: LogManager) -> bool:
        result = True
        if type(self.active) != bool:
            log.log_error('The value of "{}" has to be of type bool. Error occured in profile: {}'. format(PROFILE_ACTIVE, self.id))
            result = False
        
        if not type(self.ignore) == list:
            log.log_error('The value of "{}" has to be of type list. Error occured in profile: {}'. format(PROFILE_IGNORE, self.id))
            result = False
        
        if not type(self.source) == list:
            log.log_error('The value of "{}" has to be of type list. Error occured in profile: {}'. format(PROFILE_SOURCE, self.id))
            result = False
        else:
            if len(self.source) == 0:
                log.log_error('Please define "{}" in profile: {}'. format(PROFILE_SOURCE, self.id))
                result = False

        return result        
    


class Destination:

    def __init__(self):
        self.active: bool = False
        self.id: str = ''
        self.directory: str = ''    
        self.days_to_keep: int = -1    

    def is_valid(self, log: LogManager) -> bool:
        import os
        result = True
        if type(self.active) != bool:
            log.log_error('The value of "{}" has to be of type bool. Error occured in destination index: {}'. format(PROFILE_ACTIVE, self.id))
            result = False

        if not type(self.directory) == str:
            log.log_error('The value of "{}" has to be of type str. Error occured in destination index: {}'. format(DESTINATION_DIRECTORY, self.id))
            result = False
        else:
            if self.directory == '':
                log.log_error('Please define "{}" in destination index: {}'.format(DESTINATION_DIRECTORY, self.id))
                result = False
            else:     
                if not os.access(os.path.dirname(self.directory), os.W_OK):
                    log.log_error('Write privileges are not given at destination {}: {}. Error occured in destination index: {}'.format(DESTINATION_DIRECTORY, self.directory, self.id))
                    result = False
        
        return result


class ConfigObject:

    def __init__(self, config_filepath: str, log: LogManager):
        # accept input
        self.log = log
        self.config_filepath = config_filepath

        # load config file and translate into dictionaries
        self.log.log_hint('\nLoading and parsing config file.')
        configs = self._loadConfigs()
        self.profiles: dict[str, Profile] = self._extract_profiles(configs)
        self.destinations: dict[str, Destination] = self._extract_destinations(configs)


    def _loadConfigs(self) -> dict:
        # load the json config-file data into a dictionary
        from .utils import readJson
        return readJson(self.config_filepath)
    

    def _extract_profiles(self, configs: dict) -> dict[str, Profile]:
        profiles: dict[str, Profile] = {}
        try:
            profile_list: list = configs.get(BACKUP_PROFILES)
            for i, elemnt in enumerate(profile_list):
                profile = Profile()
                profile.id = elemnt.get(PROFILE_IDENT)
                profile.active = elemnt.get(PROFILE_ACTIVE)
                profile.source = elemnt.get(PROFILE_SOURCE)
                profile.ignore = elemnt.get(PROFILE_IGNORE)

                if (profile.id is None) or (profile.id in profiles):    
                    profile.id += '_' + str(i)  

                if profile.is_valid(self.log):
                    profiles[profile.id] = profile   

            return profiles   
               
        except (KeyError, TypeError) as e:
            self.log.log_error(f'Invalid config file. Cannot parse profile section.')
            self.log.log_error('Either: Backup profiles key "{}" not found in configuration'.format(BACKUP_PROFILES))
            self.log.log_error('Or: The value for "{}" in the configuration is not s list.'.format(BACKUP_PROFILES))
            self.log.log_error(f'Error: {e}')
            return {}
        

    def _extract_destinations(self, configs: dict) -> dict[str, Destination]:
        destinations: dict[str, Destination] = {}
        try:
            destination_list: list = configs.get(BACKUP_DESTINATINS)
            for i, elemnt in enumerate(destination_list):
                destination = Destination()
                destination.id = elemnt.get(DESTINATION_IDENT)
                destination.active = elemnt.get(DESTINATION_ACTIVE)
                destination.directory = elemnt.get(DESTINATION_DIRECTORY)
                destination.days_to_keep = elemnt.get(DESTINATION_DAYS_TO_KEEP)

                if (destination.id is None) or (destination.id in destinations):
                    destination.id += '_' + str(i)  

                if destination.is_valid(self.log):
                    destinations[destination.id] = destination   

            return destinations 
                 
        except (KeyError, TypeError) as e:
            self.log.log_error(f'Invalid config file. Cannot parse destination section.')
            self.log.log_error('Either: Backup destination key "{}" not found in configuration'.format(BACKUP_DESTINATINS))
            self.log.log_error('Or: The value for "{}" in the configuration is not a list.'.format(BACKUP_DESTINATINS))
            self.log.log_error(f'Error: {e}')
            return {}    
   