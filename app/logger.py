from logging import getLogger, StreamHandler, Formatter
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler


class Logger:
    """Parent class that implements logging.

    The main use is to add logging to a child class.

    Attributes
    ----------
    self.__add_log: getLogger
        Logger object from the Python standard library - logging

    Methods
    -------
    self.add_log(self) -> getLogger
        Getter to get getLogger object in child class
    """
    def __init__(self, name: str = 'root', level_for_file: str = 'INFO', level_for_terminal: str = 'INFO'):
        # Absolute path to the !logger folder
        path = os.path.abspath(os.path.join("/", "!logger"))
        # Create a folder with logs
        os.mkdir(path) if not os.path.exists(path) else 0
        # Logger initialization
        self.__add_log: getLogger = getLogger(name)
        self.__add_log.setLevel("DEBUG")  # set root's level
        # Adding a log entry to a file in 1 file of 5Mb
        file_log: RotatingFileHandler = RotatingFileHandler(os.path.join(path, f"{name}.log"), maxBytes=5242880,
                                                            backupCount=1)
        # Set the significance level of logging to a file
        file_log.setLevel(level_for_file)
        # Setting the form in which will be written to the file
        file_log.setFormatter(jsonlogger.JsonFormatter(fmt='[%(name)s][%(asctime)s | %(levelname)s]: %(message)s',
                                                       json_ensure_ascii=False))
        # Add log output to the console
        console_out: StreamHandler = StreamHandler()
        console_out.setLevel(level_for_terminal)
        # Setting the output format to the console
        console_out.setFormatter(Formatter(fmt='[%(name)s][%(asctime)s | %(levelname)s]: %(message)s'))
        # Adding a handler to the logger
        self.__add_log.addHandler(file_log)
        self.__add_log.addHandler(console_out)

    @property
    def add_log(self) -> getLogger:
        return self.__add_log
