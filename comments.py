#!/usr/bin/env python

import argparse
from datetime import datetime
import html
import json
import os
import random
import requests
import sys
import time

current_page = 0
exported_comments_count = 0

def get_comments(username, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    params = {}

    if page:
        params['after'] = page

    response = requests.get('https://www.reddit.com/user/{}/comments/.json'.format(username), params=params, headers=headers)
    return response

def parse_comments(data):
    global exported_comments_count

    for comment in data['children']:
        comment = comment['data']

        if args.sub_filter is not None and args.sub_filter != comment['subreddit']:
            continue

        post_id = comment['link_id'].split('_')[1]
        date_created = datetime.fromtimestamp(comment['created']).strftime('%Y-%m-%d %H:%M:%S')
        body = html.unescape(comment['body'].replace('\n', '\\n'))
        result = [comment['id'], post_id, comment['link_title'], comment['subreddit'], date_created, body]

        if not args.dump:
            exported_comments_count += 1
            file_output.write('~#~'.join(result) + '\n')
            continue

        print('~#~'.join(result))

def run(username, page):
    global current_page

    response_json = get_comments(username, page)
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
        run(username, next_page)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--usernames', type=str, help='The user(s) to crawl. Separate with commas for multiple values.')
    parser.add_argument('-f', '--usernames-file', type=str, help='A file that contains the user(s) to crawl. Each value has to be in a new line.')
    parser.add_argument('-s', '--sub-filter', type=str, help='Get comments from specific sub.')
    parser.add_argument('-p', '--page-limit', type=int, help='Limit crawling to a number of pages.')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump to standard output.')
    args = parser.parse_args()

    csv_columns = ['comment_id', 'post_id', 'post_title', 'subreddit', 'date_created', 'body']

    try:
        usernames = []
        if args.usernames_file and os.path.isfile(args.usernames_file):
            usernames = open(args.usernames_file, 'r').read().splitlines()
        elif args.usernames:
            usernames = args.usernames.split(',')

        if not usernames:
            print('Define one or more usernames using -u or -f.\nCheck the help dialog for more options.')
            sys.exit(1)

        for username in usernames:
            if not args.dump:
                filename = '{}_{}.csv'.format(username, datetime.today().strftime('%Y%m%d_%H%M%S'))
                file_output = open(filename, 'a')
                file_output.write('~#~'.join(csv_columns) + '\n')
            else:
                print('~#~'.join(csv_columns))

            current_page = 0
            exported_comments_count = 0
            run(username, None)
            time.sleep(random.randint(1, 5))

            if not args.dump:
                file_output.close()
                print('{}: {} comments exported.'.format(filename, exported_comments_count))
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response_json.text[0:70]))
        sys.exit(1)

    sys.exit(0)

