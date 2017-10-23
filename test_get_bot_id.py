#!/usr/bin/python3
"""Test docstring
"""
import re
import os
import subprocess
from slackclient import SlackClient
def main():
    BOT_NAME = 'daniel.burke89'
    slack_client = SlackClient('xoxb-233770152081-Xbq4NqWfXrGM0ve1nzak64ru')
    api_call = slack_client.api_call("users.list")
    found = False
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                found = True
                #print("ID for '" + user['name'] + "' is " + user.get('id'))
                print(user)
            if 'id' in user and user.get('id') == BOT_NAME.upper():
                found = True
                print (user)
        if not found:
            print('Could not find any user with that name')
    else:
        print("could not find bot user with the name " + BOT_NAME)

if __name__ == "__main__":
    main()
