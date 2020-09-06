import threading, queue, datetime, time
import json
import os
import requests
import aiofiles
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

class ScheduleRequest(BaseModel):
    article_id: str
    api_key: str
    date: str
    time: str

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

posts = queue.PriorityQueue()


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


@app.post('/schedule/')
async def schedule_post(schedule_request: ScheduleRequest):

    # Convert str to datetime object
    scheduled_datetime_str = schedule_request.date + schedule_request.time
    scheduled_datetime = datetime.datetime.strptime(scheduled_datetime_str, '%Y-%m-%d%I:%M%p')

    # Datetime needs to be timestamp
    scheduled_datetime = scheduled_datetime.timestamp()

    # Add scheduled post to queue
    posts.put((scheduled_datetime, schedule_request.api_key, schedule_request.article_id), scheduled_datetime)

    return f'Scheduled for {scheduled_datetime}'


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == '__main__':
    # TODO: use oauth instead
    api_key = os.environ.get('DEV_API')
    if api_key == None:
        print("Error: DEV_API key not set")
        exit(0)

    # turn-on the worker thread
    threading.Thread(target=poster, daemon=True).start()

    # while True:
    #     article_id = str(_get_article_to_publish(api_key))
    #     scheduled_date = _get_scheduled_date()
    #     posts.put((scheduled_date, api_key, article_id), scheduled_date)

