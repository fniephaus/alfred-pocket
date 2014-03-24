import sys
import datetime
from pocket import Pocket, RateLimitException, AuthException
from workflow import Workflow, PasswordNotFound

CONSUMER_KEY = '25349-924436f8cc1abc8370f02d9d'
REDIRECT_URI = 'https://github.com/fniephaus/alfred-pocket'


def main(wf):
    user_input = ''.join(wf.args)

    try:
        wf.get_password('pocket_access_token')
    except PasswordNotFound:
        authorize()

    try:
        wf.get_password('pocket_access_token')
        item_list = wf.cached_data(
            'pocket_list', data_func=get_list, max_age=60)
        if item_list is None:
            wf.delete_password('pocket_access_token')
            wf.add_item('There was a problem receiving your Pocket list.',
                        'The workflow has been deauthorized automatically. Please try again!', valid=True)
        elif len(item_list) == 0:
            wf.add_item('Your Pocket list is empty!', valid=True)
        else:
            for item in item_list:
                if ('resolved_title' in item or 'given_title' in item) and 'resolved_url' in item and 'time_added' in item:
                    title = item['resolved_title'] if 'resolved_title' in item and item[
                        'resolved_title'] != '' else item['given_title']
                    time_updated = datetime.datetime.fromtimestamp(
                        int(item['time_added'])).strftime('%Y-%m-%d %H:%M')
                    subtitle = time_updated + ': ' + item['resolved_url']

                    if user_input.lower() in title.lower() or user_input.lower() in subtitle.lower():
                        wf.add_item(title, subtitle, arg=item[
                                    'resolved_url'] + ' ' + item['item_id'], valid=True)

    except PasswordNotFound:
        wf.add_item(
            'Please press enter and click on "Authorize" on Pocket\'s website',
            'Then try again...', arg=get_auth_url(wf), valid=True)

    wf.send_feedback()


def get_list():
    access_token = wf.get_password('pocket_access_token')
    try:
        pocket_instance = Pocket(CONSUMER_KEY, access_token)
        get = pocket_instance.get()
        get_list = get[0]['list']
        if get_list == []:
            return None

        # unpack and sort items
        item_list = []
        for i in reversed(sorted(get_list.keys())):
            item_list.append(get_list[i])

        return item_list
    except AuthException:
        return None


def get_auth_url(wf):
    request_token = Pocket.get_request_token(
        consumer_key=CONSUMER_KEY, redirect_uri=REDIRECT_URI)
    wf.cache_data('pocket_request_token', request_token)

    auth_url = Pocket.get_auth_url(
        code=request_token, redirect_uri=REDIRECT_URI)

    return auth_url


def authorize():
    request_token = wf.cached_data('pocket_request_token')

    if request_token:
        try:
            user_credentials = Pocket.get_credentials(
                consumer_key=CONSUMER_KEY, code=request_token)
            wf.save_password(
                'pocket_access_token', user_credentials['access_token'])

            # we don't need the cache anymore. clear it for security reasons
            wf.clear_cache()
        except RateLimitException:
            pass


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
