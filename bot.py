from concurrent.futures.thread import ThreadPoolExecutor
import os
import logging
import datetime

import requests
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

from menu import get_menu

executor = ThreadPoolExecutor(5)

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
slack_events_adapter = SlackEventAdapter(
    os.environ['SLACK_SIGNING_SECRET'],
    endpoint="/slack/events"
)

# commands
MONDAY = 'monday'
TUESDAY = 'tuesday'
WEDNESDAY = 'wednesday'
THURSDAY = 'thursday'
FRIDAY = 'friday'
SATURDAY = 'saturday'
SUNDAY = 'sunday'
TODAY = 'today'
TOMORROW = 'tomorrow'

weekdays = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY]
weekends = [SATURDAY, SUNDAY]
all_days = weekdays + weekends
relative = [TODAY, TOMORROW]


def next_day(day):
    return (day + 1) % 7


def get_date(day):
    # want nearest future date on the given day
    desired_day = all_days.index(day)
    current = datetime.date.today()
    while current.weekday() != desired_day:
        current = current.replace(day=current.day+1)
    return current


def get_actual_day(day):
    # for day = TODAY or YESTERDAY
    today = datetime.date.today().weekday()
    return all_days[today if day == TODAY else next_day(today)]


def get_cat():
    r = requests.get('https://thecatapi.com/api/images/get')
    if r.status_code == 200:
        return [{
            'image_url': r.url,
            'text': '<' + r.url + '|src>'
        }]
    return None


def get_response_with_attachments(date):
    response = "Here's what's for lunch! Yum :yum:"
    attach = []
    try:
        all_items, all_allergens, all_may_contains = get_menu(date)
    except Exception as e:
        logging.exception(e)
        response = f"Sorry, couldn't get a menu for {date.year}/{date.month}/{date.day}. Have a cat instead :cat:"
        attach = get_cat()
        return response, attach

    for item, allergens, may_contains in zip(all_items, all_allergens, all_may_contains):
        attach.append({
            'title': item,
            'fields': [
                {
                    'title': 'Allergens',
                    'value': ', '.join(a for a in allergens) if allergens else 'None',
                    'short': True
                },
                {
                    'title': 'May contain',
                    'value': ', '.join(m for m in may_contains) if may_contains else 'None',
                    'short': True
                }
            ]
        })
    return response, attach


def handle_command(command, channel):
    """
    Receives commands directed at the bot and determines if they
    are valid commands. If so, then acts on the commands. If not,
    returns back what it needs for clarification.
    """
    command = command.lower()
    response = "Not sure what you mean. Try typing a day of the week!"
    attach = None

    # weekdays
    for day in weekdays:
        if day in command:
            date = get_date(day)
            response, attach = get_response_with_attachments(date)

    # weekends
    for day in weekends:
        if day in command:
            response = "There's no lunch on the weekends! Have a cat instead :cat:"
            attach = get_cat()

    # relative
    for day in relative:
        if day in command:
            # compute which day, and handle command with that day
            actual_day = get_actual_day(day)
            handle_command(actual_day, channel)
            return  # so it doesn't post twice

    # Send response
    client.chat_postMessage(channel=channel, text=response, attachments=attach)


@slack_events_adapter.on('app_mention')
def mention(event_data):
    text = event_data['event']['text']
    channel = event_data['event']['channel']
    # use threads to ensure we respond within 3 sec
    executor.submit(handle_command, text, channel)
    logging.info(f'received message in {channel}: {text}')


@slack_events_adapter.on('error')
def error_handler(err):
    logging.error(err)


if __name__ == '__main__':
    slack_events_adapter.start(port=3000)
