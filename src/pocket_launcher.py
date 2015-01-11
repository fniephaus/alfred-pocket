import argparse
import os
import sys
import subprocess
from pocket_api import Pocket, PocketException
from pocket import refresh_list
from workflow import Workflow
from workflow.background import run_in_background

import config

WF = Workflow()


def execute():
    args = parse_args(WF.args)

    if args.query is None:
        return 0

    query = args.query.split()
    if len(query) != 2:
        return 0

    url = query[0]
    item_id = query[1]

    if args.copy:
        print set_clipboard(url)
    elif args.visit_archive:
        subprocess.call(['open', url])
        refresh_list()
        print archive_item(item_id)
    elif args.archive:
        refresh_list()
        print archive_item(item_id)
        open_alfred()
    elif args.delete:
        refresh_list()
        print delete_item(item_id)
        open_alfred()
    elif args.website:
        subprocess.call(['open', 'http://getpocket.com/a/read/%s' % item_id])
    else:
        subprocess.call(['open', url])


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--copy', dest='copy', action='store_true', default=None)
    parser.add_argument(
        '--visit-and-archive', dest='visit_archive', action='store_true', default=None)
    parser.add_argument(
        '--archive', dest='archive', action='store_true', default=None)
    parser.add_argument(
        '--delete', dest='delete', action='store_true', default=None)
    parser.add_argument(
        '--website', dest='website', action='store_true', default=None)
    parser.add_argument('query', nargs='?', default=None)
    return parser.parse_args(args)


def set_clipboard(url):
    clipboard = os.popen(
        """ osascript -e 'set the clipboard to "%s"' """ % url).readline()
    return 'Link copied to clipboard'


def archive_item(item_id):
    access_token = WF.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.archive(item_id, wait=False)
        remove_from_cache(item_id)
        return 'Link archived'
    except PocketException:
        return 'Connection error'


def delete_item(item_id):
    access_token = WF.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.delete(item_id, wait=False)
        remove_from_cache(item_id)
        return 'Link deleted'
    except PocketException:
        return 'Connection error'


def remove_from_cache(item_id):
    # remove entry in cache
    links = WF.cached_data('pocket_list', max_age=0)
    if type(links) is dict and links:
        del links[item_id]
        WF.cache_data('pocket_list', links)


def open_alfred():
    os.system(
        """ osascript -e 'tell application "Alfred 2" to run trigger "open" in workflow "com.fniephaus.pocket"' """)


if __name__ == '__main__':
    execute()
