import os
import datetime
from .utils import writeCsv

ERRORLOG_DIRECTORY = '.backup/ErrorLog'
ERRORLOG_PREFIX = 'ERROR_occured_backup'


class LogManager():

    def __init__(self, backup_time: str):
        self.backup_time: str = backup_time

    def log_error(self, msg: str):
        print('    ERROR:: {}'.format(msg))
        timestamp: str = datetime.datetime.now().strftime('%H%M%S')
        data = []
        data.append([self.backup_time, timestamp, msg])
        writeCsv(self.get_errorlog_file(), data)    


    def log_debug(self, msg: str):
        print('DEBUG:: {}'.format(msg))
        

    def log_hint(self, msg: str):
        print('{}'.format(msg))    


    def get_errorlog_file(self) -> str:
        filename = ERRORLOG_PREFIX + self.backup_time + '.log'
        error_file = os.path.join(ERRORLOG_DIRECTORY, filename)
        return error_file  
