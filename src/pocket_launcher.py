import argparse
import os
import sys
from pocket import Pocket
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
            open_url(url)
            refresh_list(wf)
            print archive_item(item_id)
            return 0
        elif args.archive:
            refresh_list(wf)
            print archive_item(item_id)
            return 0
        elif args.delete:
            refresh_list(wf)
            print delete_item(item_id)
            return 0
        elif args.deauthorize:
            wf.delete_password('pocket_access_token')
            print "Workflow deauthorized"
            return 0
        else:
            open_url(url)
            return 0


def open_url(url):
    os.system('open %s' % url)


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
    except Exception:
        return 'Connection error'


def delete_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.delete(item_id, wait=False)
        return 'Link deleted'
    except Exception:
        return 'Connection error'


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(execute))
