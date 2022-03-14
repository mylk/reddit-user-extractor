#!/usr/bin/env python

from datetime import datetime
import json
import requests
import sys
import time

# random sleep
# convert new line
# write to file

username = 'spez'
page_number = 0
page_limit = 2

def get_comments(page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    params = {}

    if page:
        params['after'] = page

    response = requests.get('https://www.reddit.com/user/{}/comments/.json'.format(username), params=params, headers=headers)
    return response

def parse_comments(response_json):
    global page_number

    print('==================================================================================================')

    response = json.loads(response_json.text)
    data = response['data'] if 'data' in response else None

    if None:
        return

    page_number += 1

    next_page = data['after']
    for comment in data['children']:
        date_created = datetime.fromtimestamp(comment['data']['created']).strftime('%Y-%m-%d %H:%M:%S')
        print('{} ({}): {}'.format(comment['data']['id'], date_created, comment['data']['body'][0:100]))

    if page_number < page_limit:
        time.sleep(2)
        run(next_page)

def run(page):
    response_json = get_comments(page)
    parse_comments(response_json)

if __name__ == '__main__':
    try:
        run(None)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response_json.text[0:70]))
        sys.exit(1)

    sys.exit(0)

