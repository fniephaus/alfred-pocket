import argparse
import os
import subprocess
from pocket_api import Pocket, PocketException
from pocket import refresh_list
from workflow import Workflow

import config

WF = Workflow()
POCKET_URL = 'http://getpocket.com/a/read/%s'


def execute():
    args = parse_args(WF.args)

    if args.query is None:
        print "No argument provided"
        return 0

    url = args.query

    if args.visit_archive:
        subprocess.call(['open', url])
        refresh_list()
        print archive_item(url)
    elif args.archive:
        refresh_list()
        print archive_item(url)
        open_alfred()
    elif args.favorite:
        refresh_list()
        print favorite_item(url)
        open_alfred()
    elif args.delete:
        refresh_list()
        print delete_item(url)
        open_alfred()
    elif args.website:
        subprocess.call(['open', POCKET_URL % get_id(url)])
    else:
        print "An error occured"


def get_id(url):
    links = WF.cached_data('pocket_list', max_age=0)
    if links is None:
        return None
    for link in links.values():
        if url == link['given_url']:
            return link['item_id']
    return None


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--visit-and-archive', dest='visit_archive',
                        action='store_true', default=None)
    parser.add_argument('--archive', dest='archive', action='store_true',
                        default=None)
    parser.add_argument('--favorite', dest='favorite', action='store_true',
                        default=None)
    parser.add_argument('--delete', dest='delete', action='store_true',
                        default=None)
    parser.add_argument('--website', dest='website', action='store_true',
                        default=None)
    parser.add_argument('query', nargs='?', default=None)
    return parser.parse_args(args)


def archive_item(url):
    item_id = get_id(url)
    if not item_id:
        return '"item_id" not found'
    access_token = WF.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.archive(item_id, wait=False)
        remove_from_cache(item_id)
        return 'Link archived'
    except PocketException:
        return 'Connection error'


def favorite_item(url):
    item_id = get_id(url)
    if not item_id:
        return '"item_id" not found'
    access_token = WF.get_password('pocket_access_token')
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        pocket_instance.favorite(item_id, wait=False)
        return 'Link favorited'
    except PocketException:
        return 'Connection error'


def delete_item(url):
    item_id = get_id(url)
    if not item_id:
        return '"item_id" not found'
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
    if type(links) is dict and item_id in links:
        del links[item_id]
        WF.cache_data('pocket_list', links)


def open_alfred():
    os.system("osascript -e 'tell application \"Alfred 3\" to run trigger "
              "\"open\" in workflow \"com.fniephaus.pocket\"'")


if __name__ == '__main__':
    execute()
