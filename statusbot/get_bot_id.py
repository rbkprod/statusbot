#!/usr/bin/python3
"""Test docstring
"""
import re
import os
import subprocess
from slackclient import SlackClient
slack_client = SlackClient(os.environ.get('SLACK_CLIENT'))
api_call = slack_client.api_call('users.list', presence=False)
users = api_call.get('members')
def audit_sheet(names):
    found = False
    for sheet_name in names:
        found = False
        for user in users:
            if 'name' in user and user.get('name').lower() == sheet_name.lower() and (not user.get('deleted')):
                found = True
                print(user.get('name') + '\t' + user.get('id'))
        if not found:
            print(sheet_name + '\tMissmatch')
def test_user(userinfo):
    found = False
    for user in users:
        if 'name' in user and user.get('name').lower() == userinfo.lower():
            found = True
            print(user)
        if 'id' in user and user.get('id') == userinfo.upper():
            found = True
            print(user)
        if found:
            break
    if not found:
        print('Could not find any user with that name')
if not api_call.get('ok'):
    print('There was a problem connecting to the slack client')
