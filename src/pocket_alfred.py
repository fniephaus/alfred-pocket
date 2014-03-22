import sys
from pocket import Pocket, RateLimitException
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
        for item in item_list.values():
            if user_input in item['resolved_title']:
                wf.add_item(item['resolved_title'], item[
                            'resolved_url'], arg=item['resolved_url'] + ' ' + item['item_id'], valid=True)

    except PasswordNotFound:
        wf.add_item(
            'Please press enter and click on "Authorize" on Pocket\'s website',
            'Then try again...', arg=get_auth_url(wf), valid=True)

    wf.send_feedback()


def get_list():
    access_token = wf.get_password('pocket_access_token')
    pocket_instance = Pocket(CONSUMER_KEY, access_token)
    get = pocket_instance.get(
        state='unread', sort='newest', detailType='simple')
    return get[0]['list']


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
        except RateLimitException:
            pass


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
