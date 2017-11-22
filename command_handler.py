"""
Command handler module for statusbot.
Command dictionary defined at the bottom of file
"""
#!/usr/bin/env python3
import re
import logging
import pybots_data
CMDLOGGER = logging.getLogger('statusbot.command_handler')
def popdb_command():
    if pybots_data.populate_db_id(False):
        return ':white_check_mark: redis db populated.'
    else:
        return 'Something went wrong, check logs.'
def get_list_command(listname):
    try:
        lst = pybots_data.get_list(listname[2])
        if len(lst) <= 0:
            response = 'No users found'
        else:
            response = 'The following users are on the {} list:\r\n'.format(listname[2])
            for item in lst:
                response = response + "<@" + item + ">\r\n"
        return response
    except Exception:
        return 'Something went wrong, check logs.'
def help_command():
    return ('Commands available: \r\n'
            '`help`: this menu\r\n'
            '`status` [username] : checks the status for username'
            ', if no username specified, the username of the caller is used\r\n'
           )
def get_status(command):
    print('get status command')
    try:
        otheruser = command[2]
        temp_user_id = re.sub(r'[<@>]', '', otheruser).upper()
    except IndexError:
        #no other user specified
        temp_user_id = command[0]
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
def call_command(command, caller_id):
    """
    Command handler for statusbot.
    Reguired paramters: command, slack user ID (of caller).
    Example usage: call_command('getlist wban', '@USERID').
    Function returns the data from individual functions themselves.
    """
    commands = command.split(' ')
    #insert the caller as [0], always
    #[0] caller id [1] command [2] extra information
    commands.insert(0, caller_id)
    return COMMANDS.get(commands[1])(commands)
def main():
   # print(call_command('status @U7UQ54876', '@jdhsjdh'))
   print(call_command('getlist wban', '@TESTID'))
COMMANDS = {'status' : get_status, 'help' : help_command,
            'popdb' : popdb_command, 'getlist' : get_list_command}
if __name__ == "__main__":
    main()
#    text = COMMANDS.get('help')()
