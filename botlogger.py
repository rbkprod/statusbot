#!/usr/bin/env python3
import logging
from sys import platform
def configure():
    """
    This function configures a log file.
    File location will be different depending
    on which OS is detected
    """
    try:
        if platform == 'linux':
            logging.basicConfig(format='%(asctime)s %(message)s',
                                filename='/home/ubuntu/statusbot/statusbot.log',
                                level=logging.DEBUG)
        else:
            logging.basicConfig(format='%(asctime)s %(message)s',
                                filename='C:/temp/statusbot.log',
                                level=logging.DEBUG)
        logging.info('Logging configured')
    except (FileNotFoundError, PermissionError) as error:
        print('Could not configure logging: {}'.format(error))
