import os
import json
import requests

if __name__ == '__main__':
    # TODO: use oauth instead
    api_key = os.environ.get('DEV_API')
    if api_key == None:
        print("Error: DEV_API key not set")
        exit(0)

    unpublished = requests.get('https://dev.to/api/articles/me/unpublished',\
                                headers={'api_key': api_key})
    # TODO: check for errors
    content = unpublished.json()
    for i, article in enumerate(content):
        print(i, article['title'])

    # TODO: check for errors
    choice = int(input())

    chosen_article = content[choice]
    chosen_article['published'] = 'true'
    print(chosen_article)

    publish = requests.put('https://dev.to/api/articles/'+str(chosen_article['id'])+'/',\
                            headers={'api_key': api_key, 'content-type': 'application/json'},\
                            data=json.dumps({'published': 'true'}))

    print(publish.json())

