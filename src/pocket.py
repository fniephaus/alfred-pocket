import datetime
import subprocess
from time import sleep

from pocket_api import Pocket, RateLimitException
from workflow import Workflow, PasswordNotFound
from workflow.background import run_in_background, is_running

from pocket_errors import ERROR_MESSAGES
import config


CATEGORIES = ['My List', 'Favorites', 'My Tags', 'Archive', 'Articles',
              'Videos', 'Images']
ACTIONS = [x.replace(' ', '').lower() for x in CATEGORIES]
REQUIRED_KEYS = ['item_id', 'given_title', 'given_url', 'time_added']

# GitHub repo for self-updating
GITHUB_UPDATE_CONF = {'github_slug': 'fniephaus/alfred-pocket'}
# GitHub Issues
HELP_URL = 'https://github.com/fniephaus/alfred-pocket/issues'

WF = Workflow(update_settings=GITHUB_UPDATE_CONF, help_url=HELP_URL)


def main(_):
    if WF.first_run:
        WF.clear_cache()

    register_magic_arguments()

    # Get user input
    user_input = ''
    if len(WF.args):
        user_input = WF.args[0].split(' ')

    if WF.update_available:
        WF.add_item(
            'An update is available!',
            autocomplete='workflow:update',
            valid=False
        )

    try:
        WF.get_password('pocket_access_token')
    except PasswordNotFound:  # pragma: no cover
        authorize()

    try:
        WF.get_password('pocket_access_token')

        error = WF.cached_data('pocket_error', max_age=3600)
        if error and error in ERROR_MESSAGES:
            msg = ERROR_MESSAGES[error]
            WF.add_item(msg[0], msg[1], icon=get_icon('alert'),
                        valid=False)

        if (not user_input[0] or
                (len(user_input) == 1 and user_input[0].startswith('in:'))):
            for category, action in zip(CATEGORIES, ACTIONS):
                WF.add_item(category,
                            autocomplete='in:%s ' % action,
                            valid=False)
        else:
            links = get_links()
            if not links:
                WF.add_item(
                    'Your Pocket list is empty!',
                    icon=get_icon('info'),
                    valid=False
                )
            elif user_input[0] == 'in:mytags':
                tags = WF.cached_data('pocket_tags', max_age=120)
                if tags:
                    user_tag = user_input[1].strip('#')
                    if user_tag in tags:
                        links = [l for l in links.values()
                                 if 'tags' in l and user_tag in l['tags']]
                        add_items(links, ' '.join(user_input[2:]))
                    else:
                        for tag in tags:
                            if user_tag not in tag:
                                continue
                            WF.add_item('#%s' % tag,
                                        autocomplete='in:mytags #%s' % tag,
                                        valid=False)
            else:
                if user_input[0].startswith('in:'):
                    category = user_input[0][3:]
                    user_input = ' '.join(user_input[1:])
                    if category in ACTIONS:
                        links = [l for l in links.values()
                                 if item_matches(category, l)]
                else:
                    user_input = ' '.join(user_input)
                    links = links.values()
                add_items(links, user_input)

        # Update Pocket list in background
        if not WF.cached_data_fresh('pocket_list', max_age=10):
            refresh_list()

    except PasswordNotFound:  # pragma: no cover
        subprocess.call(['open', get_auth_url()])

    WF.send_feedback()


def register_magic_arguments():
    WF.magic_prefix = 'wf:'

    def delete_access_token():
        WF.delete_password('pocket_access_token')
        return 'Access token has been deleted successfully.'
    WF.magic_arguments['deauth'] = delete_access_token


def get_links(tries=10):
    links = WF.cached_data('pocket_list', max_age=120)

    # Wait for data
    while links is None:
        refresh_list()
        sleep(0.5)
        links = WF.cached_data('pocket_list', max_age=120)
        if tries > 0:
            tries -= 1
        else:
            return {}
    return links


def item_matches(category, item):
    if category == 'mylist':
        return item['status'] == '0'
    if category == 'favorites':
        return item['favorite'] == '1'
    if category == 'archive':
        return item['status'] == '1'
    if category == 'articles':
        return 'is_article' in item and item['is_article'] == '1'
    if category == 'videos':
        return 'has_video' in item and item['has_video'] == '1'
    if category == 'images':
        return 'has_image' in item and item['has_image'] == '1'


def add_items(links, user_input):
    links = sorted(links, key=lambda x: int(x['time_added']), reverse=True)
    links_count = len(links)
    for index, link in enumerate(links):
        if all(x in link for x in REQUIRED_KEYS):
            title = get_title(link)
            subtitle = get_subtitle(
                links_count - index,
                link['time_added'],
                link['given_url'],
                link['tags'] if 'tags' in link else None
            )

            if (user_input.lower() in title.lower() or
                    user_input.lower() in subtitle.lower()):
                WF.add_item(
                    title,
                    subtitle,
                    arg=link['given_url'],
                    valid=True
                )
    if WF._items == []:
        WF.add_item(
            'No links found for "%s".' % user_input,
            valid=False
        )


def get_title(link):
    for field in ['resolved_title', 'given_title', 'given_url']:
        title = link.get(field)
        if title:
            return title


def get_subtitle(item_count, time_updated, given_url, tags=None):
    time_updated = datetime.datetime.fromtimestamp(
        int(time_updated)).strftime('%Y-%m-%d %H:%M')
    short_url = given_url.replace(
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


def authorize():  # pragma: no cover
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


def refresh_list():  # pragma: no cover
    if not is_running('pocket_refresh'):
        cmd = ['/usr/bin/python', WF.workflowfile('pocket_refresh.py')]
        run_in_background('pocket_refresh', cmd)


def get_icon(name):
    name = '%s-dark' % name if is_dark() else name
    return 'icons/%s.png' % name


def is_dark():
    rgb = [int(x) for x in WF.alfred_env['theme_background'][5:-6].split(',')]
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255 < 0.5


if __name__ == '__main__':
    WF.run(main)  # pragma: no cover
