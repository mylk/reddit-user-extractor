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

    # set parameter to go to specific page of comments
    if page:
        params['after'] = page

    response = requests.get('https://www.reddit.com/user/{}/comments/.json'.format(username), params=params, headers=headers)

    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response.text[0:70]))
        return []

def parse_comments(data):
    comments = []

    for comment in data['children']:
        comment = comment['data']

        if args.sub_filter is not None and args.sub_filter != comment['subreddit']:
            continue

        # remove the content type
        post_id = comment['link_id'].split('_')[1]
        date_created = datetime.fromtimestamp(comment['created']).strftime('%Y-%m-%d %H:%M:%S')
        body = html.unescape(comment['body'].replace('\n', '\\n'))
        comments.append([comment['id'], post_id, comment['link_title'], comment['subreddit'], date_created, body])

    return comments

def run(username, page):
    global current_page
    global exported_comments_count

    response = get_comments(username, page)

    # exit if no comments in page
    data = response['data'] if 'data' in response else None
    if data is None:
        return

    comments = parse_comments(data)
    for comment in comments:
        if not args.dump:
            exported_comments_count += 1
            file_output.write('{}\n'.format('~#~'.join(comment)))
            continue

        print('~#~'.join(comment))

    current_page += 1
    next_page = data['after']

    # didn't reach the first comment or the page limit (if set)
    if next_page is not None and (args.page_limit is None or current_page < args.page_limit):
        # wait for a random number of seconds to avoid getting blocked
        time.sleep(random.randint(1, 5))
        # recurse for the next page
        run(username, next_page)

def get_usernames():
    usernames = []

    if args.usernames_file and os.path.isfile(args.usernames_file):
        with open(args.usernames_file, 'r') as usernames_file:
            usernames = usernames_file.read().splitlines()
            usernames_file.close()
    elif args.usernames:
        usernames = args.usernames.split(',')

    return usernames

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--usernames', type=str, help='The user(s) to crawl. Separate with commas for multiple values.')
    parser.add_argument('-f', '--usernames-file', type=str, help='A file that contains the user(s) to crawl. Each value has to be in a new line.')
    parser.add_argument('-s', '--sub-filter', type=str, help='Get comments from specific sub.')
    parser.add_argument('-p', '--page-limit', type=int, help='Limit crawling to a number of pages.')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump to standard output.')
    args = parser.parse_args()

    csv_columns = ['comment_id', 'post_id', 'post_title', 'subreddit', 'date_created', 'body']

    # get a usernames array, even from the parameter or the file
    usernames = get_usernames()

    if not usernames:
        print('Define one or more usernames using -u or -f.\nCheck the help dialog for more options.')
        sys.exit(1)

    for username in usernames:
        current_page = 0
        exported_comments_count = 0

        if not args.dump:
            filename = '{}_{}.csv'.format(username, datetime.today().strftime('%Y%m%d_%H%M%S'))
            file_output = open(filename, 'a')
            file_output.write('~#~'.join(csv_columns) + '\n')

            run(username, None)

            file_output.close()
            print('{}: {} comments exported.'.format(filename, exported_comments_count))
        else:
            print('~#~'.join(csv_columns))
            run(username, None)
            print('')

    sys.exit(0)

