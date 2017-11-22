#!/usr/bin/env python3
"""
Data objects for python bots
"""
from __future__ import print_function
import os
import logging
import datetime
import httplib2
import redis
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

PYBLOGGER = logging.getLogger('statusbot.pybots_data')
__version__ = "1.0.0"
try:
    import argparse
    FLAGS = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    FLAGS = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

POOL = redis.ConnectionPool(host='localhost', decode_responses=True, port=6379, db=1)
RDS = redis.StrictRedis(connection_pool=POOL)

SLACKUSERS = {}

class RangeDict(dict):
    """
    extended dict class in order to use ranges as keys
    shamelessly stolen from S.O.
    """
    def __getitem__(self, item):
        if not isinstance(item, range):
            for key in self:
                if item in key:
                    return self[key]
        else:
            return super().__getitem__(item)
POINTS_T = RangeDict({range(20, 31) : 1, range(31, 41) : 2, range(41, 51) : 3,
                      range(51, 61) : 4, range(61, 71) : 5, range(71, 81) : 6,
                      range(81, 91) : 7, range(91, 100) : 8, range(100, 101) : 9})

def get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    PYBLOGGER.info('Getting google credentials...')
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if FLAGS:
            credentials = tools.run_flow(flow, store, FLAGS)
        PYBLOGGER.info('Storing credentials to %s', credential_path)
    return credentials
def get_data():
    """
    Grabs the information from the google sheet.
    Returns tuple, empty if an error occured
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                     'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discovery_url)
    spreadsheet_id = '1NFxhHbvz0XPo7L6sxKIHoNzUmIkla_wqDs4bKr7qiHA'
    range_name = 'Sheet1!A2:J'
    values = []
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
    except Exception as err:
        PYBLOGGER.error('There was an error opening the gsheet: %s', err)
    return values
def get_status_by_id(username):
    """
    returns python dictionary of requested user hash
    """
    return RDS.hgetall(username)
def weekly_banlist(key='defaultkey'):
    """
    adds a user to the ban set
    """
    RDS.sadd('weekly_ban_list', key)
def banlist(key='defaultkey'):
    """
    adds a user to the ban set
    """
    RDS.sadd('banlist', key)
def get_list(typ='warn'):
    """
    Returns the redis list for the following:
    ''warn'' : users on the warning list
    ''wban'' : users on the weekly ban list
    ''ban''  : users on the ban list
    """
    list_types = {'warn' : 'warnlist', 'wban' : 'weekly_ban_list',
                  'ban' : 'banlist', 'prob' : 'problemlist'}
    return RDS.smembers(list_types.get(typ))
    #if typ == 'warn':
    #    return RDS.smembers('warnlist')
    #elif typ == 'wban':
    #    return RDS.smembers('weekly_ban_list')
    #elif typ == 'ban':
    #    return RDS.smembers('banlist')
    #elif typ == 'prob':
    #    return RDS.smembers('problemlist')
def warnlist(key='defaultkey', delete=False):
    """
    adds a user to the warning set
    """
    if delete:
        RDS.srem('warnlist', key)
    else:
        RDS.sadd('warnlist', key)
def process_points(username, perc, chatstring):
    """
    increases points for specific user, based on the % value and point lookup in POINTS_T
    """
    PYBLOGGER.info('Processing points for %s', username)
    try:
        get_acc = POINTS_T[int(perc)]
        slack_id = RDS.get(username)
        if slack_id:
            RDS.hincrby(slack_id, 'points', get_acc)
            RDS.hset(slack_id, 'infraction', chatstring)
            RDS.hset(slack_id, 'last_updated', datetime.datetime.now())
            current_points = int(RDS.hget(slack_id, 'points'))
            if current_points >= 9 and current_points < 18:
                warnlist(slack_id)
            elif current_points >= 18 and current_points < 27:
                weekly_banlist(slack_id)
            elif current_points >= 27:
                banlist(slack_id)
            return (slack_id, get_acc)
        else:
            RDS.sadd('problemlist', username)
            raise ValueError('Slack ID not found')
    except Exception as incr_error:
        PYBLOGGER.info('Could not increase points for %s : %s', username, incr_error)
        return None, 0
def update_user(**kwargs):
    """
    Basic function to update user info.
    Fields required: user_id, new_points, new_infr, new_wrn
    """
    PYBLOGGER.info('Updating user information')
    try:
        user_id = kwargs.get('key', None)
        new_points = kwargs.get('points')
        new_infr = kwargs.get('infraction')
        new_wrn = kwargs.get('warning')
        if not user_id or not new_points or not new_infr or not new_wrn:
            raise ValueError('Fields missing in update: {}'.format(kwargs))
        RDS.hmset(user_id, {'infraction' : new_infr,
                            'points' : new_points,
                            'last_updated' : datetime.datetime.now(),
                            'warning' : new_wrn})
    except ValueError as err:
        PYBLOGGER.error('Could not update user: %s', err)
def populate_db_id(flush=False):
    """
    flushes and populates the redis db, using slack ID as
    the identifier
    """
    PYBLOGGER.info('Populate_db called, getting values from google sheets')
    values = get_data()
    if not values:
        return False
    if flush:
        RDS.flushdb()
        for row in values:
            user_id = row[7].strip()
            if not user_id.startswith('missmatch'):
                try:
                    #cinf = get_status(usr)
                    RDS.hmset(user_id, {'infraction' : 'No infraction found',
                                        'points' : 0,
                                        'last_updated' : datetime.datetime.now(),
                                        'warning' : False,
                                        'username' : row[0].strip(),
                                        'instagram_handle' : row[8].strip()})
                    RDS.set(row[8].strip(), user_id)
                except IndexError as indx_err:
                    PYBLOGGER.error('error adding user : %s to redis : %s',
                                        row[0].strip(), indx_err)
                except redis.exceptions.ConnectionError as con_err:
                    PYBLOGGER.error('redis db connection failed: %s', con_err)
                    return False
    else:
        for row in values:
            user_id = row[7].strip()
            if not user_id.startswith('missmatch'):
                try:
                    cud = get_status_by_id(user_id)
                    cpts = cud.get('points', 0)
                    cinf = cud.get('infraction', 'No infraction found')
                    cwrn = cud.get('warning', False)
                    RDS.hmset(user_id, {'infraction' : cinf,
                                        'points' : cpts,
                                        'last_updated' : datetime.datetime.now(),
                                        'warning' : cwrn,
                                        'username' : row[0].strip(),
                                        'instagram_handle' : row[8].strip()})
                    RDS.set(row[8].strip(), user_id)
                except IndexError as indx_err:
                    PYBLOGGER.error('error adding user : %s to redis : %s',
                                        row[0].strip(), indx_err)
                except redis.exceptions.ConnectionError as con_err:
                    PYBLOGGER.error('redis db connection failed: %s', con_err)
                    return False
    return True
