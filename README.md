# statusbot
Python statusbot for Instagram Pod Community

# Requirements
Install the following services
- Python 3
- Redis (defaults to db=1)

# Python modules
Install the following modules via pip
- SlackClient
- redis
- Google Spreadsheets

# Setup
Create the following environment variables:
- SLACK_CLIENT='[your api auth key]'
- STATUSBOTID='[@id of your bot ID from slack]'

Note: Use get_bot_id.py to retrieve the slack ID given app name
