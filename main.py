import threading, queue, datetime, time
import json
import os
import requests


posts = queue.PriorityQueue()


def _get_scheduled_date():
    # TODO: uncomment
    # year = int(input('Year: '))
    # month = int(input('Month: '))
    # day = int(input('Day: '))
    # hour = int(input('Hour (UTC): '))

    #FIXME: remove minute (only for testing)
    minute = int(input('Minute: '))

    #TODO: queue with all schedules
    #TODO: remove test datetime
    # scheduled_date = datetime.datetime(year, month, day, hour, minute, \
    #                                    tzinfo=datetime.timezone.utc)
    scheduled_date = datetime.datetime(2020, 9, 4, 15, minute)
    print('Scheduled for', scheduled_date.timestamp())
    return scheduled_date.timestamp()


def _get_article_to_publish(api_key):
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


def _publish_article(api_key, article_id: str, scheduled_date):
    publish = requests.put('https://dev.to/api/articles/'+article_id+'/',\
                            headers={'api_key': api_key, 'content-type': 'application/json'},\
                            data=json.dumps({'published': 'true'}))
    print(publish.json())



def poster():
    while True:
        (scheduled_date, api_key, article_id) = posts.get()
        now = datetime.datetime.utcnow().timestamp()

        print(f"Trying {scheduled_date} at {now}")

        if scheduled_date <= now:
            print(f'Publishing {article_id}')
            _publish_article(api_key, article_id, scheduled_date)
            posts.task_done()
        else:
            posts.put((scheduled_date, api_key, article_id), scheduled_date)

        time.sleep(5)


if __name__ == '__main__':
    # TODO: use oauth instead
    api_key = os.environ.get('DEV_API')
    if api_key == None:
        print("Error: DEV_API key not set")
        exit(0)

    # turn-on the worker thread
    threading.Thread(target=poster, daemon=True).start()

    while True:
        article_id = str(_get_article_to_publish(api_key))
        scheduled_date = _get_scheduled_date()
        posts.put((scheduled_date, api_key, article_id), scheduled_date)

