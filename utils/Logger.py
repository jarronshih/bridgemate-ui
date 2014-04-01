# -*- coding: utf-8 -*-
import logging
import os
from utils.Tools import get_project_file_path

__logger__ = None

def init_logger(project_name):
    global __logger__

    __logger__ = logging.getLogger(project_name)
    __logger__.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s - %(funcName)s] %(message)s @%(filename)s(%(lineno)d)')

    # Set console to INFO level
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    __logger__.addHandler(console)


    # Set .log file to DEBUG level
    logfile = logging.FileHandler( get_project_file_path(project_name, 'log.txt') )
    logfile.setLevel(logging.DEBUG)
    logfile.setFormatter(formatter)
    __logger__.addHandler(logfile)

    return __logger__

def get_logger():
    global __logger__
    return __logger__

