import datetime
import subprocess
from time import sleep

from pocket_api import Pocket, RateLimitException
from workflow import Workflow, PasswordNotFound
from workflow.background import run_in_background, is_running

from pocket_errors import ERROR_MESSAGES
import config


WF = Workflow(update_settings={
    'github_slug': 'fniephaus/alfred-pocket',
    'version': 'v3.1',
})

def main():
    register_magic_arguments()
    user_input = WF.args[0]

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
        links = get_links()

        if links:
            if links not in ERROR_MESSAGES.keys():
                add_items(links, user_input)
            else:
                msg = ERROR_MESSAGES[item_list]
                WF.add_item(msg[0], msg[1], valid=False)
        else:
            WF.add_item('Your Pocket list is empty!', valid=False)

        # Update Pocket list in background
        if not WF.cached_data_fresh('pocket_list', max_age=10):
            refresh_list()

    except PasswordNotFound:
        subprocess.call(['open', get_auth_url()])

    WF.send_feedback()


def register_magic_arguments():
    WF.magic_prefix = 'wf:'
    def delete_access_token():
        WF.delete_password('pocket_access_token')
        return 'Access token has been deleted successfully.'
    WF.magic_arguments['deauth'] = delete_access_token


def get_links():
    links = WF.cached_data('pocket_list', max_age=120)
    tries = 10
    # Wait for data
    while(links == None):
        refresh_list()
        sleep(0.5)
        links = WF.cached_data('pocket_list', max_age=120)
        if tries > 0:
            tries -= 1
        else:
            return None
    return links


def add_items(links, user_input):
    links = sorted(links.values(), key=lambda x: int(x['item_id']), reverse=True)
    for index, link in enumerate(links):
        required_keys = [
            'item_id', 'given_title', 'resolved_url', 'time_added']
        if all(x in link for x in required_keys):
            # prepare title
            if len(link.get('resolved_title', '')) > 0:
                title = link['resolved_title']
            else:
                title = link['given_title']
            # prepare subtitle
            link_count = len(links) - index
            tags = link['tags'] if 'tags' in link else None
            subtitle = get_subtitle(
                link_count,
                link['time_added'],
                link['resolved_url'],
                tags
            )
            # prepare argument
            argument = '%s %s' % (
                link['resolved_url'], link['item_id'])

            if (user_input.lower() in title.lower() or
                    user_input.lower() in subtitle.lower()):
                WF.add_item(
                    title,
                    subtitle,
                    arg=argument,
                    valid=True
                )

    if WF._items == []:
        WF.add_item(
            'No links found for "%s".' % user_input,
            valid=False
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
