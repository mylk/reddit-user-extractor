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
exported_posts_count = 0

def get_data(username, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    params = {}

    # set parameter to go to specific page of posts
    if page:
        params['after'] = page

    response = requests.get('https://www.reddit.com/user/{}/.json'.format(username), params=params, headers=headers)

    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response.text[0:70]))
        return []

def parse_data(data):
    posts = []

    for post in data['children']:
        if post['kind'] != 't3':
            continue

        post = post['data']

        if args.sub_filter is not None and args.sub_filter != post['subreddit']:
            continue

        # remove the content type
        post_id = post['name'].split('_')[1]
        date_created = datetime.fromtimestamp(post['created']).strftime('%Y-%m-%d %H:%M:%S')
        body = html.unescape(post['selftext'].replace('\n', '\\n'))
        posts.append([post_id, post['author'], post['title'], post['subreddit'], str(post['link_flair_text']), date_created, post['url'], body])

    return posts

def run(username, page):
    global current_page
    global exported_posts_count

    response = get_data(username, page)

    # exit if no data in page
    data = response['data'] if 'data' in response else None
    if data is None:
        return

    posts = parse_data(data)
    for post in posts:
        if not args.dump:
            exported_posts_count += 1
            file_output.write('{}\n'.format('~#~'.join(post)))
            continue

        print('~#~'.join(post))

    current_page += 1
    next_page = data['after']

    # didn't reach the first post or the page limit (if set)
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
    parser.add_argument('-u', '--usernames', type=str, help='The user(s) to extract the data. Separate with commas for multiple values.')
    parser.add_argument('-f', '--usernames-file', type=str, help='A file that contains the user(s) to extract the data. Each value has to be in a new line.')
    parser.add_argument('-s', '--sub-filter', type=str, help='Filter user\'s data to specific subreddit.')
    parser.add_argument('-p', '--page-limit', type=int, help='The number of pages to examine.')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump to standard output.')
    args = parser.parse_args()

    csv_columns = ['id', 'username', 'title', 'subreddit', 'flair', 'date_created', 'url', 'body']

    # get a usernames array, even from the parameter or the file
    usernames = get_usernames()

    if not usernames:
        print('Define one or more usernames using -u or -f.\nCheck the help dialog for more options.')
        sys.exit(1)

    if args.dump:
        print('~#~'.join(csv_columns))

    for username in usernames:
        current_page = 0
        exported_posts_count = 0

        if not args.dump:
            filename = '{}_posts_{}.csv'.format(username, datetime.today().strftime('%Y%m%d_%H%M%S'))
            file_output = open(filename, 'a')
            file_output.write('~#~'.join(csv_columns) + '\n')

            run(username, None)

            file_output.close()
            print('{}: {} posts exported.'.format(filename, exported_posts_count))
        else:
            run(username, None)

    sys.exit(0)

