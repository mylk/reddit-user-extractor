#!/usr/bin/env python

from datetime import datetime
import html
import random
import sys
import time

import common

current_page = 0
exported_count = 0

def parse_data(data):
    comments = []

    for comment in data['children']:
        comment = comment['data']

        if args.sub_filter is not None and comment['subreddit'] not in args.sub_filter.split(','):
            continue

        # remove the content type
        post_id = comment['link_id'].split('_')[1]
        date_created = datetime.fromtimestamp(comment['created']).strftime('%Y-%m-%d %H:%M:%S')
        body = html.unescape(comment['body'].replace('\n', '\\n'))
        comments.append([comment['id'], comment['author'], post_id, comment['link_title'], comment['subreddit'], date_created, body])

    return comments

def run(username, page):
    global current_page
    global exported_count

    response = common.get_data(common.URL_COMMENTS, username, page)

    # exit if no comments in page
    data = response['data'] if 'data' in response else None
    if data is None:
        return

    comments = parse_data(data)
    for comment in comments:
        if not args.dump:
            exported_count += 1
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

if __name__ == '__main__':
    args = common.setup_arguments()

    csv_columns = ['comment_id', 'username', 'post_id', 'post_title', 'subreddit', 'date_created', 'body']

    # get a usernames array, even from the parameter or the file
    usernames = common.get_usernames(args)

    if not usernames:
        print('Define one or more usernames using -u or -f.\nCheck the help dialog for more options.')
        sys.exit(1)

    if args.dump:
        print('~#~'.join(csv_columns))

    for username in usernames:
        current_page = 0
        exported_count = 0

        if not args.dump:
            filename = '{}_comments_{}.csv'.format(username, datetime.today().strftime('%Y%m%d_%H%M%S'))
            file_output = open(filename, 'a')
            file_output.write('~#~'.join(csv_columns) + '\n')

            run(username, None)

            file_output.close()
            print('{}: {} comments exported.'.format(filename, exported_count))
        else:
            run(username, None)

    sys.exit(0)

