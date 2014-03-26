import sys
import os
from pocket import Pocket
from requests.exceptions import ConnectionError
from workflow import Workflow
import argparse
import config


def execute(wf):
    parser = argparse.ArgumentParser()
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

    query = args.query.split()
    if len(query) > 0:
        url = query[0]
    if len(query) > 1:
        item_id = query[1]

    if args.visit_archive:
        open_url(url)
        wf.clear_cache()
        print archive_item(item_id)
        return 0
    elif args.archive:
        wf.clear_cache()
        print archive_item(item_id)
        return 0
    elif args.delete:
        wf.clear_cache()
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


def archive_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.archive(item_id, wait=False)
        return 'Link archived'
    except ConnectionError:
        return 'Connection error'


def delete_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.delete(item_id, wait=False)
        return 'Link deleted'
    except ConnectionError:
        return 'Connection error'


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(execute))
