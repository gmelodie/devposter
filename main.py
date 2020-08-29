import datetime
import json
import os
import requests
import sched
import time

def get_scheduled_date():
    year = int(input('Year: '))
    month = int(input('Month: '))
    day = int(input('Day: '))
    hour = int(input('Hour (UTC): '))

    #FIXME: remove minute (only for testing)
    minute = int(input('Minute: '))

    #TODO: queue with all schedules
    #TODO: error check (earlier dates)
    scheduled_date = datetime.datetime(year, month, day, hour, minute, \
                                       tzinfo=datetime.timezone.utc)
    print('Scheduled for', scheduled_date)
    return scheduled_date.timestamp()


def get_article_to_publish(api_key):
    unpublished = requests.get('https://dev.to/api/articles/me/unpublished',\
                                headers={'api_key': api_key})
    # TODO: check for errors
    content = unpublished.json()
    for i, article in enumerate(content):
        print(i, article['title'])

    # TODO: check for errors
    choice = int(input())
    chosen_article = content[choice]
    print(chosen_article['title'], chosen_article['id'])

    return chosen_article['id']


def publish_article(api_key, article_id: str):
    publish = requests.put('https://dev.to/api/articles/'+article_id+'/',\
                            headers={'api_key': api_key, 'content-type': 'application/json'},\
                            data=json.dumps({'published': 'true'}))
    print(publish.json())


if __name__ == '__main__':
    # TODO: use oauth instead
    api_key = os.environ.get('DEV_API')
    if api_key == None:
        print("Error: DEV_API key not set")
        exit(0)

    chosen_article_id = get_article_to_publish(api_key)
    scheduled_date = get_scheduled_date()

    poster = sched.scheduler(time.time, time.sleep)
    poster.enterabs(scheduled_date, 1, publish_article, argument=(api_key, str(chosen_article_id)))
    poster.run()

