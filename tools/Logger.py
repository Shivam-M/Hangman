from datetime import datetime
from sys import exc_info


class Logger:
    def __init__(self):
        pass

    @staticmethod
    def log(LOG_MESSAGE, LOG_TYPE="INFO"):
        TIME_PREFIX = str(datetime.now().strftime('%H:%M:%S'))
        print(f'[{TIME_PREFIX}] {LOG_TYPE}: {LOG_MESSAGE}')

    @staticmethod
    def error(exception):
        exc_type, value, exc_traceback = exc_info()
        TIME_PREFIX = str(datetime.now().strftime('%H:%M:%S'))
        ERROR_TYPE = str(exc_type).strip('<class \'').strip('\'>')
        ERROR_INFO = value
        ERROR_LINE = exc_traceback.tb_lineno
        print(f'[{TIME_PREFIX}] {ERROR_TYPE}: [{ERROR_LINE}] {ERROR_INFO}')


if __name__ == '__main__':
    Logger.log('Test event.', 'ERROR')
