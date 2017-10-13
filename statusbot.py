#!/usr/bin/ python3
"""
    A basic status bot to check infracions for the
    user calling 'status'
"""
import time
import re
import datetime
import os
import threading
from collections import deque
import pybots_data
#import redis
from slackclient import SlackClient

STATUS_BOT_ID = "<@" + os.environ.get('STATUSBOTID') + ">"
STATUS_COMMAND = "status"
HELP_COMMAND = "help"
AUDIT_COMMAND = "audit"
POP_DB = "popdb"
REFULIST_COMMAND = "populist"
#RDS = redis.Redis(host='localhost', port=6379, password=None)
SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))
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

def process_warning_messages():
    pass
def process_user_names(id, name=None):
    pass

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
            if pybots_data.process_points(chatstring):
                time.sleep(0.5)
                INFR_QUEUE.remove(chatstring)
            else:
                print('Error processing points for string : {}'.format(chatstring))
                INFR_QUEUE.remove(chatstring)

def main():
    """
    Starts the bot by connecting to slack using the
    SlackClient API
    """
    create_user_list(True)

    print(str(datetime.datetime.today()) + ' Connecting...', end=' ')
    read_websocket_delay = 1
    if SLACK_CLIENT.rtm_connect():
        print('@statusbot connected and running')
        rtmthread = bThread(1, 'rtmThread')
        rtmthread.start()
        while True:
            command, channel, user_id = parse_slack_output(SLACK_CLIENT.rtm_read())
            if command and channel and user_id:
                handle_command(command, channel, user_id)
            time.sleep(read_websocket_delay)
    else:
        print(str(datetime.datetime.today()) + ' \nConnection failed, please check tokens')

def create_user_list(to_pybots=False):
    """
        docstring to be compiled
    """
    api_call = SLACK_CLIENT.api_call('users.list', presence=False)
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
                    data[user_id] = [user_name, is_admin]
            pybots_data.SLACKUSERS = data
            return True
    except IndexError as index_error:
        print('Error in create_user_list: {}'.format(index_error))
        return False
def get_user_info(**kwargs):
    """
    Does a call to the slack api to get all users
    and iterates through to find the username of
    the user_id calling the status bot
    """
    user_id = kwargs.get('user_id', None)
    user_name = kwargs.get('user_name', None)
    is_admin = False
    if user_id:
        user_id = user_id.upper()
        #get user from dict based on ID
        user_data = pybots_data.SLACKUSERS.get(user_id)
        return(user_data[0], user_data[1])
        #for user in get_user_list():
        #    if 'id' in user and user.get('id') == user_id:
        #        return (user['name'], user['is_admin'])
    elif user_name:
        found = False
        for key, value in pybots_data.SLACKUSERS.items():
            for item in value:
                if item == user_name:
                    user_id = key
                    if isinstance(value[1], bool):
                        is_admin = value[1]
                        found = True
            if found:
                return (user_id, is_admin)
     #   ivd = {v: k for k, v in pybots_data.SLACKUSERS.items()}
     #   user_data = ivd.get(user_name)
     #   for user in get_user_list():
     #       if 'name' in user and user.get('name') == user_name:
     #           return (user['id'], user['is_admin'])
    return (None, None)

def handle_command(command, channel, user_id):
    """
    Recevies commands from users directed at bot
    """
    time_start = time.time()
    temp_user_id = user_id
    print(str(datetime.datetime.today()) + ' User id: ' + user_id + ' initaited command: ' +
          command + ', finding user name of requestor...', end=' ')
    requestor_name, is_admin = get_user_info(user_id=user_id)
    print('done, user name is: ' + requestor_name)
    response = 'Not a valid command, why don''t you try `help`'
    if command.startswith(HELP_COMMAND):
        response = ('Commands available: \r\n'
                    '`help`: this menu\r\n'
                    '`popdb`: flush and re-populate db data\r\n'
                    '`populist`: flush and re-populate the slack user list\r\n'
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
    # if command.starstwith(AUDIT_COMMAND):
    #    audit_information = ''
    #    response = 'Audit for ' + user_name + ' completed: ' + audit_information
    if command.startswith(STATUS_COMMAND):
        otheruser = command.split('status')[1].strip()
        if otheruser:
            if '<@' in otheruser:
                temp_user_id = re.sub(r'[<@>]','',otheruser)
                requestor_name, is_admin = get_user_info(user_id=temp_user_id)
            else:
                temp_user_id, is_admin = get_user_info(user_name=otheruser)
                #temp_user_id = '<@' + temp_user_id.upper() + '>'
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
            response = '*Status* for <@{}> : {}'.format(temp_user_id.upper(), infraction)
    print(str(datetime.datetime.today()) + ' Sending response to SlackClient...', end=' ')
    SLACK_CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
    time_end = time.time()
    print('done.')
    print(str(datetime.datetime.today()) + ' Process took : '
          + str(time_end - time_start) + ' seconds.')

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID. Taken from:
        https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
    """
    output_list = slack_rtm_output
    valid_len = len(output_list)
    if output_list and valid_len > 0:
        for output in output_list:
            if output and 'text' in output:
                #match_audit = re.search(r'Audit for (.+) is starting', output['text'])
                match_leech = re.search(r'(.+) has leeched (\d+)', output['text'])
                if STATUS_BOT_ID in output['text']:
                    return (output['text'].split(STATUS_BOT_ID)[1].strip().lower(),
                            output['channel'], output['user'])
                elif match_leech: #and LEECH_BOT in output['text']:
                    #if match.group(1) and match.group(2):
                    print(output['text'])
                    output_list = output['text'].split('\n')
                    for x in output_list:
                        match_leech = re.search(r'(.+) has leeched (\d+)', x)
                        if match_leech:
                            if match_leech.group(1) and match_leech.group(2):
                                INFR_QUEUE.append(x)
                        #if pybots_data.process_points(match.group(1), match.group(2)):
                        #    print('Points added', output['channel'], output['user'])
    return None, None, None


def prep():
    pass
    
if __name__ == "__main__":
    prep()
    main()
