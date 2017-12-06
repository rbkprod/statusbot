"""
Command handler module for statusbot.
Command dictionary defined at the bottom of file
"""
#!/usr/bin/env python3
import re
from collections import namedtuple
import logging
#import pybots_data
from statusbot import pybots_data
Cmdtuple = namedtuple('Cmd', 'cmd caller_id is_admin params')
CMDLOGGER = logging.getLogger('statusbot.command_handler')
ADMIN_MSG = 'Only admins can do that.'
def set_command(cmd_tuple):
    if not cmd_tuple.is_admin:
        return ADMIN_MSG
    rds_commands = ('points', 'infraction')
def is_valid_command(string):
    """
    Tests a specific string to see if it's
    a valid command.
    """
    try:
        cmd = get_command(string)[0]
        if cmd in COMMANDS:
            return True
    except Exception:
        return False
def get_command(cmd_string):
    """
    Simple function to return the first string (before space)
    as index[0]. The remainder will be returned as a list that
    can be used as other params
    """
    tmp = cmd_string.split(' ')
    return (tmp[0], tmp[1:])
def popdb_command(cmd_tuple):
    """
    Validates and initiates the popdb command.
    """
    if cmd_tuple.is_admin:
        if pybots_data.populate_db_id(False):
            return ':white_check_mark: redis db populated.'
        else:
            return 'Something went wrong, check logs.'
    else:
        return ADMIN_MSG
def get_list_command(params):
    """
    Initiates the list function.
    getlist [listname]
    """
    try:
        list_name = params[3][0]
        lst = pybots_data.get_list(list_name)
        if len(lst) <= 0:
            response = 'No users found'
        else:
            response = 'The following users are on the list:\r\n'
            for item in lst:
                response = response + "<@" + item + ">\r\n"
        return response
    except (ValueError, IndexError) as list_err:
        return (str(list_err))
def help_command():
    """
    Returns help text
    """
    return ('Commands available: \r\n'
            '`help`: this menu\r\n'
            '`status` [username] : checks the status for username'
            ', if no username specified, the username of the caller is used\r\n'
           )
def get_status(command):
    """
    Initiates status check.
    If the params are omitted then the caller_id
    is used.
    """
    print('get status command')
    try:
        otheruser = command.params[0]
        temp_user_id = re.sub(r'[<@>]', '', otheruser).upper()
    except IndexError:
        #no other user specified
        temp_user_id = command.caller_id
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
        CMDLOGGER.error('Error message received : %s', err)
    return '*Status* for <@{}> : {}'.format(temp_user_id.upper(), infraction)
def create_command(command_string, caller_id, is_admin):
    """
    Returns a named tuple with command parameters
    """
    if caller_id == 'U5PU8069F':
        is_admin = True
    cmd, params = get_command(command_string)
    return Cmdtuple(cmd, caller_id, is_admin, params)
def call_command(command_string, caller_id, is_admin):
    """
    Command handler for statusbot.
    Reguired paramters: command, slack user ID (of caller), Admin Boolean
    Example usage: call_command('getlist wban', '@USERID', False).
    Returns the data from individual functions themselves.
    """
    cmd = create_command(command_string, caller_id, is_admin)
    try:
        return COMMANDS.get(cmd.cmd)(cmd)
    except (TypeError, IndexError) as err:
        CMDLOGGER.info('There was a problem issuing the command : %s, Error : %s',
                       command_string, err)
        return 'There was a problem issuing the command.'
def main():
    """
    Main()
    """
    # print(call_command('status @U7UQ54876', '@jdhsjdh'))
    print('Testing a basic command...')
    print(call_command('list sdadasd', 'U5PU8069F', False))
#Commands dictionary, used to get the corresponding function
#for the command that was issued
COMMANDS = {'status' : get_status, 'help' : help_command,
            'popdb' : popdb_command, 'list' : get_list_command,
            'set' : set_command}
if __name__ == "__main__":
    main()
