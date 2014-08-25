from pocket import Pocket, AuthException
from workflow import Workflow, PasswordNotFound

import config


def get_list(wf, access_token):
    pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
    try:
        get = pocket_instance.get(sort='newest')
        get_list = get[0]['list']
        if get_list == []:
            return None

        # Unpack and sort items
        item_list = []
        for item in sorted(get_list.values(), key=lambda x: int(x['time_added']), reverse=True):
            item_list.append(item)

        return item_list

    except AuthException:
        return 'error1'
        wf.delete_password('pocket_access_token')
        wf.logger.error(
            'There was a problem receiving your Pocket list. The workflow has been deauthenticated automatically. Please try again!')
    except Exception:
        return 'error2'
        wf.logger.error(
            'Could not contact getpocket.com. Please check your Internet connection and try again!')

    return None

if __name__ == '__main__':
    wf = Workflow()

    try:
        access_token = wf.get_password('pocket_access_token')

        def wrapper():
            return get_list(wf, access_token)

        wf.cached_data('pocket_list', data_func=wrapper, max_age=1)

    except PasswordNotFound:
        wf.logger.error('Password not found!')
