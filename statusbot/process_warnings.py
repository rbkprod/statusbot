#!/usr/bin/env python3
"""
Module to send DMs to users, at current will process
warnings and update user info in redis
"""
import os
from os import path
import logging
from sys import platform
#import pybots_data
from statusbot import pybots_data
from slackclient import SlackClient

LOG_FILENAME = '/process_warnings.log'
LOG_PATHS = {'linux' : '/home/ubuntu/logs/', 'win32' : 'C:/temp/'}
LOGGER = logging.getLogger('statusbot.process_warnings')
LOGGER.setLevel(logging.INFO)
FILE_HANDLE = logging.FileHandler(LOG_PATHS.get(platform, path.expanduser('~')) + LOG_FILENAME)
FILE_HANDLE.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
FILE_HANDLE.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLE)
SEND = True
UPDATE = True

SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))
DEFAULT_WARNING = ('*WARNING*: You have leeched more than *50%* in' +
                   ' a group that you''ve posted in.' +
                   ' Be sure to comment on *all* posts within'+
                   ' the group(s) you have decided to post into.'+
                   ' You can check your current infraction' +
                   ' level by calling @statusbot status.')
def report_warnings():
    lst = pybots_data.get_list('warn')
    response = 'The following users have been issued warnings:'
    for i in lst:
        response = response + ' ' + i
    send_message('G7A9PQ74G', response)
    lst = pybots_data.get_list('wban')
    for i in lst:
        response = response + i
    return(response)
def send_message(user_id, response=DEFAULT_WARNING):
    """
    Sends a DM to the user with text = response
    """
    LOGGER.info('Sending %s to user id: %s', response, user_id)
    SLACK_CLIENT.api_call("chat.postMessage", channel=user_id, text=response,
                          as_user=True, username='statusbot')
def run():
    """
    main function for processing warnings
    """
    LOGGER.info('Processing warnings started : SEND: %s, UPDATE: %s', SEND, UPDATE)
    users = pybots_data.get_list('warn')
    for user_id in users:
        try:
            status_info = pybots_data.get_status_by_id(user_id)
            LOGGER.info('Slack ID: %s, User: %s',
                        user_id, status_info.get('username', 'Not found'))
            if status_info.get('warning', False):
                response = ('*WARNING*: Please note that your current infraction ' +
                            'level is `' +  status_info.get('points')  +
                            '`, and as such you run the risk of being banned.' +
                            ' Be sure to comment on *all* posts within'+
                            ' the group(s) you have decided to post into.')
                if SEND:
                    send_message(user_id, response)
                if UPDATE:
                    pybots_data.update_user(key=user_id,
                                            warning=True,
                                            infraction='Warning Issued.',
                                            points=status_info.get('points'))
                    pybots_data.del_user_from_list(user_id, status_info.get('points'))
            else:
                LOGGER.info('Could not process warning for : %s', user_id)
            print('Processed user : {}'.format(user_id))
        except Exception as err:
            LOGGER.error('There was a problem issuing warnings: %s', err)
    LOGGER.info('done')

# if __name__ == "__main__":
#     main()
