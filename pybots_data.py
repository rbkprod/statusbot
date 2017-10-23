#!/usr/bin/env python3
"""
    data objects for pyhton bots
"""
from __future__ import print_function
import os
import datetime
import re
import httplib2
import redis
import botlogger
from botlogger import logging
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

__version__ = "1.0.0"
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

POOL = redis.ConnectionPool(host='localhost', decode_responses=True, port=6379, db=0)
RDS = redis.StrictRedis(connection_pool=POOL)

SLACKUSERS = {}

class RangeDict(dict):
    """
    extended dict class in order to use ranges as keys
    shamelessly stolen from S.O.
    """
    def __getitem__(self, item):
        if type(item) != range:
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
    logging.info('Getting google credentials...')
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
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        logging.info(str(datetime.datetime.today()) + ' Storing credentials to ' + credential_path)
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
    except Exception as e:
        logging.error('There was an error opening the gsheet: {}'.format(e))
    return values

def get_status(username):
    """
    returns python dictionary of requested user hash
    """
    return RDS.hgetall(username)
def weekly_banlist(key = 'defaultkey'):
    """
    adds a user to the ban set
    """
    RDS.sadd('weekly_ban_list', key)
def banlist(key = 'defaultkey'):
    """
    adds a user to the ban set
    """
    RDS.sadd('banlist', key)
def warnlist(key = 'defaultkey'):
    """
    adds a user to the warning set
    """
    RDS.sadd('warnlist', key)
def process_points(chatstring):
    """
    increases points for specific user, based on the % value and point lookup in POINTS_T
    """
    match = re.search(r'(.+) has leeched (\d+)', chatstring)
    username, perc = match.group(1), match.group(2)

    get_acc = POINTS_T[int(perc)]
    try:
        RDS.hincrby(username, 'points', get_acc)
        RDS.hset(username, 'infraction', chatstring)
        RDS.hset(username, 'last_updated', datetime.datetime.now())
        current_points = int(RDS.hget(username, 'points'))
        if current_points >= 9 and current_points < 18:
            warnlist(username)
        elif current_points >= 18 and current_points < 27:
            weekly_banlist(username)
        elif current_points >= 27:
            banlist(username)
        return True
    except Exception as incr_error:
        logging.error('Could not increase points for {} : {}'.format(username, incr_error))
    return False

def populate_db(flush = False):
    """
        flushes and populates the redis db
    """
    logging.info('Populate_db called, getting values from google sheets')
    values = get_data()
    if not values:
        return False
    #rds = redis.Redis(host='localhost', port=6379, password=None)
    #rds.flushdb()
    if flush:
        RDS.flushdb()
    for row in values:
        usr = row[0].strip()
        infr = 'No infraction found'
        try:
            infr = row[7]
        except IndexError:
            pass
        try:
            cud = get_status(usr)
            cpts = cud.get('points', 0)
            cinf = cud.get('infraction', infr)
            cwrn = cud.get('warning', False)
            #cinf = get_status(usr)
            RDS.hmset(usr, {'infraction' : cinf,
                            'points' : cpts,
                            'reason' : 'none',
                            'last_updated' : datetime.datetime.now(),
                            'warning' : cwrn})
        except redis.exceptions.ConnectionError as con_err:
            logging.error('redis db connection failed: ' + con_err)
            return False
    return True
