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
from collections import deque
import pybots_data
import process_warnings
from slackclient import SlackClient

STATUS_BOT = os.environ.get('STATUSBOTID')
STATUS_BOT_ID = "<@" + STATUS_BOT + ">"
LEECH_BOT = 'U6ESUDNHE'
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))

COMMANDS = ['status', 'help', 'popdb', 'populist', 'warnlist', 'wbanlist']
STATUS_COMMAND = "status"
HELP_COMMAND = "help"
POP_DB = "popdb"
REFULIST_COMMAND = "populist"
WARNLIST_COMMAND = 'warnlist'
WEEKLY_BL_COMMAND = 'wbanlist'
INFR_QUEUE = deque([])

def write_to_queue(queue, chatstring):
    """
    adds a infraction string
    to the queue
    """
    queue.put(chatstring)
    logger.info('Process %s wrote text to queue: %s', os.getpid(), chatstring)
def read_from_queue(queue):
    """
    Gets data from queue and processes the points
    """
    #while True:
    while True:
        chatstring = queue.get()
        print('Process %s read text from reader: %s', os.getpid(), chatstring)
        #logger.info('Process {} read text from reader: {}'.format(os.getpid(), chatstring))
        match = re.search(r'(.+) has leeched (\d+)', chatstring)
        username, perc = match.group(1), match.group(2)
        user_id, pts = pybots_data.process_points(username, perc, chatstring)
        if pts >= 4:
            process_warnings.send_message(user_id)
        time.sleep(0.2)
        if queue.empty():
            break
def main():
    """
    Starts the bot by connecting to slack using the
    SlackClient API
    """
    create_user_list(True)
    print('Connecting...', end=' ')
    logger.info('Connecting...')
    read_websocket_delay = 1
    if SLACK_CLIENT.rtm_connect():
        print('@statusbot connected and running')
        logger.info('@statusbot connected and running')
        #user_id, pts = pybots_data.process_points('ruan.bekker', '51','test from main')
        #if pts >= 4:
        #    process_warnings.send_message(user_id)
        while True:
            command, channel, user_id, queue = parse_slack_output(SLACK_CLIENT.rtm_read())
            if command and channel and user_id:
                if command in COMMANDS or re.search(r'status <@.+', command):
                    handle_command(command, channel, user_id)
            if queue:
                logger.info('Processing items in queue')
                reader_p = Process(target=read_from_queue, args=((queue),))
                reader_p.start()
                #reader_p.join()
            time.sleep(read_websocket_delay)
    else:
        print(' \nConnection failed, please check tokens')

def create_user_list(to_pybots=False):
    """
        This function is called ad-hoc and on startup
        in order to create a dictionary of slack users.
        The slack api call is slow and will probably need
        pagination in the future
    """
    api_call = SLACK_CLIENT.api_call('users.list', presence=False)
    logger.info('Creating user list')
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
        logger.error('Error in create_user_list: %s', index_error)
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
        logger.info('get_user_info returned: %s and %s', user_data[0], user_data[1])
        return(user_data[0], user_data[1])
    elif user_name:
        logger.info('Attempting to get user by dict values')
        found = False
        for key, value in pybots_data.SLACKUSERS.items():
            for item in value:
                if item == user_name:
                    user_id = key
                    if isinstance(value[1], bool):
                        is_admin = value[1]
                        found = True
            if found:
                logger.info('get_user_info returned: %s and %s', user_id, is_admin)
                return (user_id, is_admin)
    return (None, None)
def handle_command(command, channel, user_id):
    """
    Recevies commands from users directed at bot
    """
    time_start = time.time()
    temp_user_id = user_id
    print('User id: ' + user_id + ' initaited command: ' +
          command + ', finding user name of requestor...', end=' ')
    logger.info('User id: %s initaited command: %s' +
                ' finding user name of requestor...', user_id, command)
    requestor_name, is_admin = get_user_info(user_id=user_id)
    print('done, user name is: ' + requestor_name)
    response = 'Not a valid command, why don''t you try `help`'
    #Refactor this junk!
    if command.startswith(HELP_COMMAND):
        response = ('Commands available: \r\n'
                    '`help`: this menu\r\n'
                    '`status` [username] : checks the status for username'
                    ', if no username specified, the username of the caller is used\r\n'
                   )
    if command.startswith(WEEKLY_BL_COMMAND):
        lst = pybots_data.get_list('wban')
        if len(lst) <= 0:
            response = 'No users found'
        else:
            response = 'The following users are on the weekly ban list:\r\n'
            for item in lst:
                response = response + "<@" + item + ">\r\n"
    if command.startswith(WARNLIST_COMMAND):
        lst = pybots_data.get_list('warn')
        if len(lst) <= 0:
            response = 'No users found'
        else:
            response = 'The following users are on the warning list:\r\n'
            for item in lst:
                response = response + "<@" + item + ">\r\n"
    if command.startswith(REFULIST_COMMAND):
        if not is_admin and requestor_name != 'ruan.bekker':
            response = 'Only admins can do that.'
        else:
            if create_user_list(True):
                response = ':white_check_mark: slack user list populated.'
            else:
                response = 'Something went wrong, check logs'
    if command.startswith(POP_DB):
        if not is_admin and requestor_name != 'ruan.bekker':
            response = 'Only admins can do that.'
        else:
            if pybots_data.populate_db_id(False):
                response = ':white_check_mark: redis db populated.'
            else:
                response = 'Something went wrong, check logs.'
    if command.startswith(STATUS_COMMAND):
        otheruser = command.split('status')[1].strip()
        if otheruser:
            temp_user_id = re.sub(r'[<@>]', '', otheruser).upper()
        try:
            inf_data = pybots_data.get_status_by_id(temp_user_id)
            if inf_data:
                last_updated = str(inf_data.get('last_updated', '`Error retrieving last updated`'))
                infraction = ('`' + inf_data.get('infraction', '`Error retrieving infraction`') + '`' +
                              '. *Points:* ' + '`' + inf_data.get('points', '`Error retrieving points`')
                              + '`' + '. *Last upated:* ' + '`' +  last_updated[:20] + '`')
            else:
                raise ValueError('Could not locate user in db')
        except (Exception) as err:
            infraction = ('Status not found, the most likely cause is a missmatch '
                          'between the Google Sheet & Slack *usernames*.')
            logger.error('Error message received : %s', err)
        response = '*Status* for <@{}> : {}'.format(temp_user_id.upper(), infraction)
    print('Sending response to SlackClient...', end=' ')
    logger.info('Sending response to SlackClient...')
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    time_end = time.time()
    print('done.')
    logger.info('done.')
    print('Process took : '
          + str(time_end - time_start) + ' seconds.')
    logger.info('Process took : '
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
        logger.info(chatstring)
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
                    logger.error('Error parsing output: %s -> %s ',
                                 parse_error, output['text'])
    return None, None, None, None
if __name__ == "__main__":
    #botlogger.configure()
    filename = '/statusbot.log'
    file_paths = {'linux' : '/home/ubuntu/statusbot/', 'win32' : 'C:/temp/'}
    logger = logging.getLogger('statusbot')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(file_paths.get(platform, path.expanduser('~')) + filename)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    main()
