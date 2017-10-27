#! /usr/bin/env python3
import os
#import pybots_data
import statusbot
from statusbot import pybots_data
from slackclient import SlackClient

SLACK_CLIENT = SlackClient(os.environ.get('SLACK_CLIENT'))

def main():
    users = pybots_data.getwarnlist()
    slack_users = statusbot.create_user_list(True)
    for user in users:
        status_info = pybots_data.get_status(user)
        user_slack_id = pybots_data.SLACKUSERS.get(user, None)
        if user_slack_id:
            response = ('WARNING: Please note that your current infraction ' +
                        'level is `' +  status_info.get('points', 9)  +
                        '`, and as such you run the risk of being banned.'
                        ' Please contribute to this community by commenting on posts.')
            SLACK_CLIENT.api_call("chat.postMessage", channel=user_slack_id, text=response,
                                as_user=True, username='statusbot')
        print(user)

if __name__ == "__main__":
    main()