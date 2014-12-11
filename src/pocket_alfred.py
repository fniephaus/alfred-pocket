import datetime
import sys
import subprocess
from time import sleep
from pocket import Pocket, RateLimitException
from workflow import Workflow, PasswordNotFound
from workflow.background import run_in_background, is_running

import config


WF = Workflow(update_settings={
    'github_slug': 'fniephaus/alfred-pocket',
    'version': 'v3.1',
})

ERROR_MESSAGES = {
    'AuthException': [
        'There was a problem receiving your Pocket list...',
        'The workflow has been deauthorized automatically. Please try again!'
    ],
    'URLError': [
        'Could not connect to getpocket.com...',
        'Please check your Internet connection and try again!'
    ],
    'PocketException': [
        'Could not receive your Pocket list...',
        'Please try again or file a bug report!'
    ]
}


def main():
    user_input = ''.join(WF.args)

    if WF.update_available:
        WF.add_item(
            "An update is available!",
            autocomplete='workflow:update',
            valid=False
        )

    try:
        WF.get_password('pocket_access_token')
    except PasswordNotFound:
        authorize()

    try:
        WF.get_password('pocket_access_token')
        item_list = get_item_list() or 'Error'

        if len(item_list) == 0:
            WF.add_item('Your Pocket list is empty!', valid=False)
        elif item_list in ERROR_MESSAGES.keys():
            msg = ERROR_MESSAGES[item_list]
            WF.add_item(msg[0], msg[1], valid=False)
        else:
            add_items(item_list, user_input)

        # Update Pocket list in background
        if not WF.cached_data_fresh('pocket_list', max_age=10):
            refresh_list()

    except PasswordNotFound:
        subprocess.call(['open', get_auth_url()])

    WF.send_feedback()


def get_item_list():
    item_list = WF.cached_data('pocket_list', max_age=120)
    tries = 10
    # Wait for data
    while(item_list == None):
        refresh_list()
        sleep(0.5)
        item_list = WF.cached_data('pocket_list', max_age=120)
        if tries > 0:
            tries -= 1
        else:
            return None
    return item_list


def add_items(item_list, user_input):
    for index, item in enumerate(reversed(item_list)):
        required_keys = [
            'item_id', 'given_title', 'resolved_url', 'time_added']
        if all(x in item for x in required_keys):
            # prepare title
            if len(item.get('resolved_title', '')) > 0:
                title = item['resolved_title']
            else:
                title = item['given_title']
            # prepare subtitle
            item_count = len(item_list) - index
            tags = item['tags'] if 'tags' in item else None
            subtitle = get_subtitle(
                item_count,
                item['time_added'],
                item['resolved_url'],
                tags
            )
            # prepare argument
            argument = '%s %s' % (
                item['resolved_url'], item['item_id'])

            if (user_input.lower() in title.lower() or
                    user_input.lower() in subtitle.lower()):
                WF.add_item(
                    title,
                    subtitle,
                    arg=argument,
                    valid=True
                )


def get_subtitle(item_count, time_added, resolved_url, tags=None):
    time_updated = datetime.datetime.fromtimestamp(
        int(time_added)).strftime('%Y-%m-%d %H:%M')
    short_url = resolved_url.replace(
        'http://', '').replace('https://', '')

    subtitle_elements = ['#%s' % item_count, time_updated, short_url]

    if tags:
        tags = ['#%s' % x for x in tags.keys()]
        subtitle_elements.insert(2, ', '.join(tags))

    return ' - '.join(subtitle_elements)


def get_auth_url():
    request_token = Pocket.get_request_token(
        consumer_key=config.CONSUMER_KEY, redirect_uri=config.REDIRECT_URI)
    WF.cache_data('pocket_request_token', request_token)

    auth_url = Pocket.get_auth_url(
        code=request_token, redirect_uri=config.REDIRECT_URI)

    return auth_url


def authorize():
    request_token = WF.cached_data('pocket_request_token')
    if request_token:
        try:
            user_credentials = Pocket.get_credentials(
                consumer_key=config.CONSUMER_KEY,
                code=request_token
            )
            WF.save_password(
                'pocket_access_token',
                user_credentials['access_token']
            )
            # We don't need the cache anymore. Clear it for security reasons
            WF.clear_cache()
        except RateLimitException:
            WF.logger.error('RateLimitException')


def refresh_list():
    if not is_running('pocket_refresh'):
        cmd = ['/usr/bin/python', WF.workflowfile('pocket_refresh.py')]
        run_in_background('pocket_refresh', cmd)


if __name__ == '__main__':
    main()
