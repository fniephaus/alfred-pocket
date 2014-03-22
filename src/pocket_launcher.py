import sys
import os
import json
from pocket import Pocket
from workflow import Workflow
import argparse

CONSUMER_KEY = '25349-924436f8cc1abc8370f02d9d'


def execute(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--visit', dest='visit', action='store_true', default=None)
    parser.add_argument(
        '--archive', dest='archive', action='store_true', default=None)
    parser.add_argument(
        '--delete', dest='delete', action='store_true', default=None)
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)

    query = args.query.split()
    url = query[0]
    if len(query) > 1:
        item_id = query[1]

    if len(query) == 1 or args.visit:
        open_url(url)
    elif args.archive:
        archive_item(item_id)
    elif args.delete:
        delete_item(item_id)
    else:
        open_url(url)
        archive_item(item_id)


def open_url(url):
    os.system('open %s' % url)


def archive_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    pocket_instance.archive(item_id, wait=False)


def delete_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    pocket_instance.delete(item_id, wait=False)


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(execute))
