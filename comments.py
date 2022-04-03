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
    for comment in data['children']:
        comment = comment['data']

        if args.sub_filter is not None and args.sub_filter != comment['subreddit']:
            continue

        date_created = datetime.fromtimestamp(comment['created']).strftime('%Y-%m-%d %H:%M:%S')
        body = html.unescape(comment['body'][0:100].replace('\n', '\\n'))
        result = [comment['id'], comment['link_id'], comment['link_title'], comment['subreddit'], date_created, body]

        if not args.dump:
            file_output.write('~#~'.join(result) + '\n')
            continue

        print('~#~'.join(result))

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
    parser.add_argument('-s', '--sub-filter', type=str, help='Get comments from specific sub')
    parser.add_argument('-p', '--page-limit', type=int, help='Limit crawling to a number of pages')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump to standard output')
    args = parser.parse_args()

    csv_columns = ['comment_id', 'post_id', 'post_title', 'subreddit', 'date_created', 'body']

    if not args.dump:
        filename = '{}_{}.csv'.format(args.username, datetime.today().strftime('%Y%m%d_%H%M%S'))
        file_output = open(filename, 'a')
        file_output.write('~#~'.join(csv_columns) + '\n')
    else:
        print('~#~'.join(csv_columns))

    try:
        run(None)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response_json.text[0:70]))
        sys.exit(1)

    if not args.dump:
        file_output.close()

    sys.exit(0)

