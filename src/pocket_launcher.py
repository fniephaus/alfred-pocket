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
        archive_item(item_id)
        print "Link archived"
        return 0
    elif args.archive:
        archive_item(item_id)
        print "Link archived"
        return 0
    elif args.delete:
        delete_item(item_id)
        print "Link deleted"
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
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    pocket_instance.archive(item_id, wait=False)


def delete_item(item_id):
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    pocket_instance.delete(item_id, wait=False)


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(execute))
