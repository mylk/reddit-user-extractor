import argparse
import json
import os
import random
import requests
import time

URL_COMMENTS = 'https://www.reddit.com/user/{}/comments/.json'
URL_ALL = 'https://www.reddit.com/user/{}/.json'

def get_data(url, username, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Accept-Encoding': 'gzip'
    }
    params = {}

    # set parameter to go to specific page of comments
    if page:
        params['after'] = page

    response = requests.get(url.format(username), params=params, headers=headers)

    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError as ex:
        print('ERROR: Cannot decode data - {}. HTTP response: \"{}\"'.format(str(ex), response.text[0:70]))
        return []

def get_usernames(args):
    usernames = []

    if args.usernames_file and os.path.isfile(args.usernames_file):
        with open(args.usernames_file, 'r') as usernames_file:
            usernames = usernames_file.read().splitlines()
            usernames_file.close()
    elif args.usernames:
        usernames = args.usernames.split(',')

    return usernames

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--usernames', type=str, help='The user(s) to extract the data. Separate with commas for multiple values.')
    parser.add_argument('-f', '--usernames-file', type=str, help='A file that contains the user(s) to extract the data. Each value has to be in a new line.')
    parser.add_argument('-s', '--sub-filter', type=str, help='Filter user\'s data to specific subreddits. Separate with commas for multiple values.')
    parser.add_argument('-p', '--page-limit', type=int, help='The number of pages to examine.')
    parser.add_argument('-d', '--dump', action='store_true', help='Dump to standard output.')

    return parser.parse_args()

