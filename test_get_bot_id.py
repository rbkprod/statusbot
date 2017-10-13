#!/usr/bin/python3
"""Test docstring
"""
import re
import os
import subprocess
from slackclient import SlackClient
def main():
    BOT_NAME = 'leech_detector'
    slack_client = SlackClient(os.environ.get('SLACK_CLIENT'))
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)

if __name__ == "__main__":
    main()
