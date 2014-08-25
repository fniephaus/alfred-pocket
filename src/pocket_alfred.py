import datetime
import sys
import subprocess
from pocket import Pocket, RateLimitException
from pocket_refresh import get_list
from workflow import Workflow, PasswordNotFound
from workflow.background import run_in_background, is_running

import config


def main(wf):
    user_input = ''.join(wf.args)

    if wf.update_available:
        subtitle = 'New: %s' % wf.update_info['body']
        wf.add_item("An update is available!", subtitle,
                    autocomplete='workflow:update', valid=False)

    try:
        wf.get_password('pocket_access_token')
    except PasswordNotFound:
        authorize()

    try:
        wf.get_password('pocket_access_token')
        item_list = wf.cached_data('pocket_list', None, max_age=0)
        if item_list is not None:
            if len(item_list) == 0:
                wf.add_item('Your Pocket list is empty!', valid=False)
            elif item_list == 'error1':
                wf.add_item(
                    'There was a problem receiving your Pocket list...',
                    'The workflow has been deauthorized automatically. Please try again!', valid=False)
            elif item_list == 'error2':
                wf.add_item(
                    'Could not connect to getpocket.com...',
                    'Please check your Internet connection and try again!', valid=False)
            else:
                for index, item in enumerate(item_list):
                    if all(x in item for x in ['item_id', 'given_title', 'resolved_url', 'time_added']):
                        item_title = item['resolved_title'] if 'resolved_title' in item and item[
                            'resolved_title'] != '' else item['given_title']
                        title = '#%s %s' % (len(item_list) - index, item_title)
                        time_updated = datetime.datetime.fromtimestamp(
                            int(item['time_added'])).strftime('%Y-%m-%d %H:%M')
                        subtitle = time_updated + ': ' + item['resolved_url']
                        argument = '%s %s' % (
                            item['resolved_url'], item['item_id'])

                        if user_input.lower() in title.lower() or user_input.lower() in subtitle.lower():
                            wf.add_item(
                                title, subtitle, arg=argument, valid=True)
        else:
            wf.add_item(
                'Could receive your Pocket list...',
                'Please try again or file a bug report!', valid=False)

        # Update Pocket list in background
        if not wf.cached_data_fresh('pocket_list', max_age=10):
            refresh_list(wf)

    except PasswordNotFound:
        subprocess.call(['open', get_auth_url(wf)])

    wf.send_feedback()


def get_auth_url(wf):
    request_token = Pocket.get_request_token(
        consumer_key=config.CONSUMER_KEY, redirect_uri=config.REDIRECT_URI)
    wf.cache_data('pocket_request_token', request_token)

    auth_url = Pocket.get_auth_url(
        code=request_token, redirect_uri=config.REDIRECT_URI)

    return auth_url


def authorize():
    request_token = wf.cached_data('pocket_request_token')

    if request_token:
        try:
            user_credentials = Pocket.get_credentials(
                consumer_key=config.CONSUMER_KEY, code=request_token)
            wf.save_password(
                'pocket_access_token', user_credentials['access_token'])

            # We don't need the cache anymore. clear it for security reasons
            wf.clear_cache()

            def wrapper():
                return get_list(wf, user_credentials['access_token'])

            wf.cached_data('pocket_list', data_func=wrapper, max_age=1)
        except RateLimitException:
            pass


def refresh_list(wf):
    if not is_running('pocket_refresh'):
        cmd = ['/usr/bin/python', wf.workflowfile('pocket_refresh.py')]
        run_in_background('pocket_refresh', cmd)


if __name__ == '__main__':
    wf = Workflow(update_config={
        'github_slug': 'fniephaus/alfred-pocket',
        'version': 'v2.2',
    })
    sys.exit(wf.run(main))
