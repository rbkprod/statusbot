"""
Module to send DMs to users, at current will process
warnings and update user info in redis
"""
#!/usr/bin/env python3
import os
import datetime
import logging
from statusbot import pybots_data
from slackclient import SlackClient

LOGGER = logging.getLogger('statusbot.process_warnings')

SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))
DEFAULT_WARNING = ('*WARNING*: You have leeched more than *50%* in' +
                   ' a group that you''ve posted in.' +
                   ' Be sure to comment on *all* posts within'+
                   ' the group(s) you have decided to post into.'+
                   ' You can check your current infraction' +
                   ' level by calling @statusbot status.')
def send_message(user_id, response=DEFAULT_WARNING):
    """
    Sends a DM to the user with text = response
    """
    LOGGER.info('Sending %s to user id: %s', response, user_id)
    SLACK_CLIENT.api_call("chat.postMessage", channel=user_id, text=response,
                          as_user=True, username='statusbot')
def main():
    """
    main function for processing warnings
    """
    LOGGER.info(str(datetime.datetime.now()) + ' Processing warnings...')
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
                            ' Be sure that you engage with all posts within'+
                            ' the group you have decided to post into' +
                            ' by commenting.')
                send_message(user_id, response)
                pybots_data.update_user(key=user_id,
                                        warning=True,
                                        infraction='Warning Issued.',
                                        points=status_info.get('points'))
                pybots_data.warnlist(user_id, True)
            else:
                LOGGER.info('Could not process warning for : %s', user_id)
            print('Processed user : {}'.format(user_id))
        except Exception as err:
            LOGGER.error('There was a problem issuing warnings: %s', err)
    LOGGER.info(str(datetime.datetime.now()) + 'done')

if __name__ == "__main__":
    main()
