from __future__ import print_function
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import logging
import json
import time

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# @app.route('/')
# def homepage():
#     return "Hi there, how ya doin?"

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_events():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    str = {'Jane, Khadeeja, Neeru'}
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    total_events = []
    mydate = datetime.datetime.now().isoformat()
    now = now = datetime.datetime.now()
    now_plus_15 = now + datetime.timedelta(minutes = 15)
    new_time = now_plus_15.isoformat()
    if not events:
        total_events.append('Joe is free') 
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        name = event['creator'].get('displayName')
        mystringbusy = name
        mystringfree = name
        activity = event['summary']
        mystringbusy += ' is busy right now. They are currently at '
        mystringbusy += activity
        mystringfree += ' will be free later'
        mystringsoon = name
        mystringsoon += ' will be busy soon'
        if mydate <= end and mydate >= start:
        	total_events.append(mystringbusy)
        else:
        	if start <= new_time:
        		total_events.append(mystringsoon)
    if not total_events:
    	total_events.append('Congrats, everyone in your contacts is free right now')
    return total_events


@ask.launch
def start_skill():
    welcome_message = 'Hello there, would you like to know if your contacts are free'
    return question(welcome_message)


@ask.intent("YesIntent")
def prompt_new_contact_name():
    # msg = render_template('prompt_for_name')
    events = get_events()
    event_msg = 'The current availabilities are {}'.format(events)
    return statement(event_msg)


@ask.intent("NoIntent")
def no_intent():
    bye_text = 'I am not sure why you asked me to run then, but okay... bye'

    msg = render_template('template_name_here', foo="bar")
    return statement(msg)


if __name__ == '__main__':
    app.run(debug=True)