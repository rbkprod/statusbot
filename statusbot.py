#!/usr/bin/env python3
"""
    A basic status bot to manage infracions for
    the Slack Instagram POD Community
"""
import time
import re
import datetime
import os
import threading
from collections import deque
import botlogger
from botlogger import logging
import pybots_data
from slackclient import SlackClient

STATUS_BOT = os.environ.get('STATUSBOTID')
STATUS_BOT_ID = "<@" + STATUS_BOT + ">"
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))

COMMANDS = ['status', 'help', 'popdb', 'populist']
STATUS_COMMAND = "status"
HELP_COMMAND = "help"
POP_DB = "popdb"
REFULIST_COMMAND = "populist"
INFR_QUEUE = deque([])
EXIT_THREAD = False
class bThread(threading.Thread):

    def __init__(self, threadid, name):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
    def run(self):
        print('Starting {}'.format(self.name))
        process_queue_data(self.name, 5)
        print('Exiting {}'.format(self.name))

def process_queue_data(threadname, delay):
    """
    this function will process items in the queue
    """
    while not EXIT_THREAD:
        while len(INFR_QUEUE) <= 0:
            time.sleep(delay)
        for chatstring in list(INFR_QUEUE):
            print('Thread: {}. Delay: {}. First Index: {}'.format(
                threadname, delay, chatstring), end='\n')
            logging.info('Thread: {}. Delay: {}. First Index: {}'.format(
                threadname, delay, chatstring))
            if pybots_data.process_points(chatstring):
                time.sleep(0.5)
                INFR_QUEUE.remove(chatstring)
            else:
                print('Error processing points for string : {}'.format(chatstring))
                logging.error('Error processing points for string : {}'.format(chatstring))
                INFR_QUEUE.remove(chatstring)
def main():
    """
    Starts the bot by connecting to slack using the
    SlackClient API
    """
    create_user_list(True)
    print(str(datetime.datetime.today()) + ' Connecting...', end=' ')
    logging.info(str(datetime.datetime.today()) + ' Connecting...')
    read_websocket_delay = 1
    if SLACK_CLIENT.rtm_connect():
        print('@statusbot connected and running')
        logging.info('@statusbot connected and running')
        rtmthread = bThread(1, 'rtmThread')
        rtmthread.start()
        while True:
            command, channel, user_id = parse_slack_output(SLACK_CLIENT.rtm_read())
            if command and channel and user_id:
                if command in COMMANDS or re.search(r'status <@.+', command):
                    handle_command(command, channel, user_id)
            time.sleep(read_websocket_delay)
    else:
        print(str(datetime.datetime.today()) + ' \nConnection failed, please check tokens')

def create_user_list(to_pybots=False):
    """
        This function is called ad-hoc and on startup
        in order to create a dictionary of slack users.
        The slack api call is slow and will probably need
        pagination in the future
    """
    api_call = SLACK_CLIENT.api_call('users.list', presence=False)
    logging.info('Creating user list')
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
                    display_name = item.get('display_name')
                    deleted = item.get('deleted')
                    if not deleted:
                        data[user_id] = [user_name, is_admin, display_name]
            pybots_data.SLACKUSERS = data
            return True
    except IndexError as index_error:
        print('Error in create_user_list: {}'.format(index_error))
        logging.error('Error in create_user_list: {}'.format(index_error))
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
        logging.info('get_user_info returned: {} and {}'.format(user_data[0], user_data[1]))
        return(user_data[0], user_data[1])
    elif user_name:
        logging.info('Attempting to get user by dict values')
        found = False
        for key, value in pybots_data.SLACKUSERS.items():
            for item in value:
                if item == user_name:
                    user_id = key
                    if isinstance(value[1], bool):
                        is_admin = value[1]
                        found = True
            if found:
                logging.info('get_user_info returned: {} and {}'.format(user_id, is_admin))
                return (user_id, is_admin)
    return (None, None)

def handle_command(command, channel, user_id):
    """
    Recevies commands from users directed at bot
    """
    time_start = time.time()
    temp_user_id = user_id
    print(str(datetime.datetime.today()) + ' User id: ' + user_id + ' initaited command: ' +
          command + ', finding user name of requestor...', end=' ')
    logging.info(str(datetime.datetime.today()) + ' User id: ' + user_id + ' initaited command: ' +
                 command + ', finding user name of requestor...')
    requestor_name, is_admin = get_user_info(user_id=user_id)
    print('done, user name is: ' + requestor_name)
    logging.info('done, user name is: ' + requestor_name)
    response = 'Not a valid command, why don''t you try `help`'
    if command.startswith(HELP_COMMAND):
        response = ('Commands available: \r\n'
                    '`help`: this menu\r\n'
                    #'`popdb`: flush and re-populate db data\r\n'
                    #'`populist`: flush and re-populate the slack user list\r\n'
                    '`status` [username] : checks the status for username'
                    ', if no username specified, the username of the caller is used\r\n'
                   )
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
            if pybots_data.populate_db():
                response = ':white_check_mark: redis db populated.'
            else:
                response = 'Something went wrong, check logs'
    if command.startswith(STATUS_COMMAND):
        otheruser = command.split('status')[1].strip()
        if otheruser:
            if '<@' in otheruser:
                temp_user_id = re.sub(r'[<@>]', '', otheruser)
                requestor_name, is_admin = get_user_info(user_id=temp_user_id)
            else:
                temp_user_id, is_admin = get_user_info(user_name=otheruser)
                user_name = otheruser
        if not temp_user_id:
            response = ('The Slack user lookup for *{}* failed. '
                        'Please ensure to use a valid user name'.format(user_name))
        else:
            try:
                inf_data = pybots_data.get_status(requestor_name)
                last_updated = str(inf_data.get('last_updated', '`Error retrieving last updated`'))
                infraction = ('`' + inf_data.get('infraction', '`Error retrieving infraction`') + '`' +
                            '. *Points:* ' + '`' + inf_data.get('points', '`Error retrieving points`')
                            + '`' + '. *Last upated:* ' + '`' +  last_updated[:20] + '`')
                if inf_data.get('reason') != 'none':
                    infraction = (infraction + '. *Reason:* ' + inf_data.get('reason'))
            except TypeError as err:
                infraction = ('Status not found, the most likely cause is a missmatch '
                            'between the Google Sheet & Slack *usernames*.')
                print('Error message received : {}'.format(err))
                logging.error('Error message received : {}'.format(err))
            response = '*Status* for <@{}> : {}'.format(temp_user_id.upper(), infraction)
    print(str(datetime.datetime.today()) + ' Sending response to SlackClient...', end=' ')
    logging.info(str(datetime.datetime.today()) + ' Sending response to SlackClient...')
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    time_end = time.time()
    print('done.')
    logging.info('done.')
    print(str(datetime.datetime.today()) + ' Process took : '
          + str(time_end - time_start) + ' seconds.')
    logging.info(str(datetime.datetime.today()) + ' Process took : '
                 + str(time_end - time_start) + ' seconds.')

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
                    match_leech = re.search(r'(.+) has leeched (\d+)', output['text'])
                    if STATUS_BOT_ID in output['text']:
                        return (output['text'].split(STATUS_BOT_ID)[1].strip().lower(),
                                output['channel'], output['user'])
                    elif (match_leech and
                          output['user'] != STATUS_BOT):
                          #do not process leech text from statusbot itself
                        print(output['text'])
                        logging.info(output['text'])
                        output_list = output['text'].split('\n')
                        for x in output_list:
                            match_leech = re.search(r'(.+) has leeched (\d+)', x)
                            if match_leech:
                                if match_leech.group(1) and match_leech.group(2):
                                    INFR_QUEUE.append(x)
                        return None, None, None
                except Exception as parse_error:
                    print('Error parsing output: {} -> {} '.format(parse_error, output['text']))
                    logging.error('Error parsing output: {} -> {} '.format
                                  (parse_error, output['text']))
    return None, None, None
if __name__ == "__main__":
    botlogger.configure()
    main()
