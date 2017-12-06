#!/usr/bin/env python3
"""
    A basic status bot to manage infracions for
    the Slack Instagram POD Community
"""
import time
import re
import os
from os import path
import logging
from sys import platform
from multiprocessing import Process, Queue
import pybots_data
import command_handler
import process_warnings
from slackclient import SlackClient

STATUS_BOT = os.environ.get('STATUSBOTID')
STATUS_BOT_ID = "<@" + STATUS_BOT + ">"
LEECH_BOT = 'U6ESUDNHE'
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))

#-----------------------------------------------
#Bot logging section:
#Declared here so that aux modules that are called
#on their own can use statusbot configured logging.
#Can refactor this later if need be
LOG_FILENAME = '/statusbot.log'
LOG_PATHS = {'linux' : '/home/ubuntu/logs/', 'win32' : 'C:/temp/'}
LOGGER = logging.getLogger('statusbot')
LOGGER.setLevel(logging.INFO)
FILE_HANDLE = logging.FileHandler(LOG_PATHS.get(platform, path.expanduser('~')) + LOG_FILENAME)
FILE_HANDLE.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
FILE_HANDLE.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLE)
#-----------------------------------------------
def write_to_queue(queue, chatstring):
    """
    adds a infraction string
    to the queue
    """
    queue.put(chatstring)
    LOGGER.info('Process %s wrote text to queue: %s', os.getpid(), chatstring)
def read_from_queue(queue):
    """
    Gets data from queue and processes the points
    """
    while True:
        chatstring = queue.get()
        print('Process %s read text from reader: %s', os.getpid(), chatstring)
        match = re.search(r'(.+) has leeched (\d+)', chatstring)
        username, perc = match.group(1), match.group(2)
        user_id, pts = pybots_data.process_points(username, perc, chatstring)
        if pts >= 4:
            process_warnings.send_message(user_id)
        time.sleep(0.2)
        if queue.empty():
            break
def create_user_list(to_pybots=False):
    """
        This function is called ad-hoc and on startup
        in order to create a dictionary of slack users.
        The slack api call is slow and will probably need
        pagination in the future
    """
    api_call = SLACK_CLIENT.api_call('users.list', presence=False)
    LOGGER.info('Creating user list')
    data = {}
    try:
        pybots_data.SLACKUSERS = {}
        if api_call.get('ok'):
            users = api_call.get('members')
            if to_pybots:
                for item in users:
                    user_id = item.get('id')
                    user_name = item.get('name')
                    is_admin = item.get('is_admin')
                    deleted = item.get('deleted')
                    if not deleted:
                        data[user_id] = [user_name, is_admin]
            pybots_data.SLACKUSERS = data
            return True
    except IndexError as index_error:
        LOGGER.error('Error in create_user_list: %s', index_error)
        return False
def get_user_info(**kwargs):
    """
    Does a dictionary lookup on user_id for user information.
    If the username was specified as opposed to the id, the
    dictionary will be 'inversed' and the id will be retrieved
    by going through the values (slower)
    """
    user_id = kwargs.get('user_id', None)
    user_name = kwargs.get('user_name', None)
    is_admin = False
    if user_id:
        user_id = user_id.upper()
        #get user from dict based on ID
        user_data = pybots_data.SLACKUSERS.get(user_id)
        LOGGER.info('get_user_info returned: %s and %s', user_data[0], user_data[1])
        return(user_data[0], user_data[1])
    elif user_name:
        LOGGER.info('Attempting to get user by dict values')
        found = False
        for key, value in pybots_data.SLACKUSERS.items():
            for item in value:
                if item == user_name:
                    user_id = key
                    if isinstance(value[1], bool):
                        is_admin = value[1]
                        found = True
            if found:
                LOGGER.info('get_user_info returned: %s and %s', user_id, is_admin)
                return (user_id, is_admin)
    return (None, None)
def handle_command(command, channel, user_id):
    """
    Recevies commands from users directed at bot
    """
    time_start = time.time()
    print('User id: ' + user_id + ' initaited command: ' +
          command + ', finding user name of requestor...', end=' ')
    LOGGER.info('User id: %s initaited command: %s' +
                ' finding user name of requestor...', user_id, command)
    requestor_name, is_admin = get_user_info(user_id=user_id)
    print('done, user name is: ' + requestor_name)
    response = command_handler.call_command(command, user_id, is_admin)
    print('Sending response to SlackClient...', end=' ')
    LOGGER.info('Sending response to SlackClient...')
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    time_end = time.time()
    print('done.')
    LOGGER.info('done.')
    print('Process took : '
          + str(time_end - time_start) + ' seconds.')
    LOGGER.info('Process took : '
                + str(time_end - time_start) + ' seconds.')
def valid_leech_admin(user):
    """
    Returns True if user is allowed to add leech
    """
    if user != STATUS_BOT and (user == LEECH_BOT or user == 'U5PU8069F'):
        return True
    return False
def handle_leech_text(chatstring, can_add_leech=False):
    """
    Tests the string for validity.
    Returns queue object
    """
    match_leech = re.search(r'(.+) has leeched (\d+)', chatstring)
    if match_leech:
        queue = Queue()
        LOGGER.info(chatstring)
        output_list = chatstring.split('\n')
        if can_add_leech:
            for string in output_list:
                if match_leech.group(1) and match_leech.group(2):
                    sub_string = re.sub(r' - This.+', '', string)
                    write_to_queue(queue, sub_string)
        return queue
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID. Taken from:
        https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
    """
    #try:
    output_list = slack_rtm_output
    valid_len = len(output_list)
    if output_list and valid_len > 0:
        for output in output_list:
            if output and 'text' in output:
                try:
                    if STATUS_BOT_ID in output['text']:
                        return (output['text'].split(STATUS_BOT_ID)[1].strip().lower(),
                                output['channel'], output['user'], None)
                    queue = handle_leech_text(output['text'], valid_leech_admin(output['user']))
                    return None, None, None, queue
                except Exception as parse_error:
                    print('Error parsing output: {} -> {} '.format(parse_error, output['text']))
                    LOGGER.error('Error parsing output: %s -> %s ',
                                 parse_error, output['text'])
    return None, None, None, None
def connect_to_slack():
    """
    Function to connect to the slack API
    """
    print('Connecting...', end=' ')
    LOGGER.info('Connecting...')
    if SLACK_CLIENT.rtm_connect():
        print('@statusbot connected and running')
        LOGGER.info('@statusbot connected and running')
        return True
    else:
        print('Cound not connect')
        return False
def main():
    """
    Starts the bot by connecting to slack using the
    SlackClient API
    """
    if connect_to_slack():
        create_user_list(True)
        read_websocket_delay = 1
        while True:
            try:
                command, channel, user_id, queue = parse_slack_output(SLACK_CLIENT.rtm_read())
                if command and channel and user_id:
                    #if command in COMMANDS or re.search(r'status <@.+', command):
                    if command_handler.is_valid_command(command):
                        handle_command(command, channel, user_id)
                if queue:
                    LOGGER.info('Processing items in queue')
                    reader_p = Process(target=read_from_queue, args=((queue),))
                    reader_p.start()
                    #reader_p.join()
                time.sleep(read_websocket_delay)
            except Exception as conn_err:
                #in the event that command handler fails - or that an invalid response
                #type is sent to slack api, this catch should stop statusbot
                #from breaking
                LOGGER.info('Error from inside main() : %s', conn_err)
                for i in range(0, 4):
                    LOGGER.info('Connection attempt %s', i)
                    if connect_to_slack():
                        break
                    LOGGER.info('Could not connect, attempting again in 20s')
                    time.sleep(20)

    else:
        print(' \nConnection failed, please check tokens')
if __name__ == "__main__":
    main()
