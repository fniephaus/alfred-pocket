import argparse
import os
import sys
import subprocess
from pocket import Pocket, PocketException
from pocket_alfred import refresh_list
from workflow import Workflow
from workflow.background import run_in_background

import config


def execute(wf):
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
        '--deauthorize', dest='deauthorize', action='store_true', default=None)
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    if args.query is not None:
        query = args.query.split()
        if len(query) > 0:
            url = query[0]
        if len(query) > 1:
            item_id = query[1]

        if args.copy:
            print set_clipboard(url)
            return 0
        elif args.visit_archive:
            subprocess.call(['open', url])
            refresh_list(wf)
            print archive_item(item_id)
            return 0
        elif args.archive:
            refresh_list(wf)
            print archive_item(item_id)
            open_alfred()
            return 0
        elif args.delete:
            refresh_list(wf)
            print delete_item(item_id)
            open_alfred()
            return 0
        elif args.deauthorize:
            wf.delete_password('pocket_access_token')
            print "Workflow deauthorized"
            open_alfred()
            return 0
        else:
            subprocess.call(['open', url])
            return 0


def set_clipboard(url):
    clipboard = os.popen(
        """ osascript -e 'set the clipboard to "%s"' """ % url).readline()
    return 'Link copied to clipboard'


def archive_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.archive(item_id, wait=False)
        return 'Link archived'
    except PocketException:
        return 'Connection error'


def delete_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.delete(item_id, wait=False)

        # remove entry in cache
        item_list = wf.cached_data('pocket_list', max_age=0)
        if type(item_list) is list and len(item_list) > 0:
            item_list[:] = [d for d in item_list if d.get('item_id') != item_id]
            wf.cache_data('pocket_list', item_list)

        return 'Link deleted'
    except PocketException:
        return 'Connection error'

def open_alfred():
    os.system( """ osascript -e 'tell application "Alfred 2" to search "pocket "' """)

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(execute))
