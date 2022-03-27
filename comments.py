#!/usr/bin/env python

import argparse
from datetime import datetime
import html
import json
import random
import requests
import sys
import time

# random sleep
# convert new line
# write to file

current_page = 0

def get_comments(page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    params = {}

    if page:
        params['after'] = page

    response = requests.get('https://www.reddit.com/user/{}/comments/.json'.format(args.username), params=params, headers=headers)
    return response

def parse_comments(data):
    print('==================================================================================================')

    for comment in data['children']:
        date_created = datetime.fromtimestamp(comment['data']['created']).strftime('%Y-%m-%d %H:%M:%S')
        print('{} ({}): {}'.format(comment['data']['id'], date_created, html.unescape(comment['data']['body'][0:100].replace('\n', '\\n'))))

def run(page):
    global current_page

    response_json = get_comments(page)
    response = json.loads(response_json.text)

    data = response['data'] if 'data' in response else None
    if data is None:
        return

    parse_comments(data)

    current_page += 1
    next_page = data['after']

    # didn't reach the first comment or the page limit (if set)
    if next_page is not None and (args.page_limit is None or current_page < args.page_limit):
        # wait for a random number of seconds to avoid get blocked
        time.sleep(random.randint(1, 5))
        run(next_page)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required=True, help='The user\'s comments to crawl')
    parser.add_argument('-p', '--page-limit', type=int, help='Limit crawling to a number of pages')
    args = parser.parse_args()

    try:
        run(None)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response_json.text[0:70]))
        sys.exit(1)

    sys.exit(0)

