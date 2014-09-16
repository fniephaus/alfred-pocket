from time import time

from pocket import Pocket, AuthException
from workflow import Workflow, PasswordNotFound

import config

LINK_LIMIT = 2000

def refresh():
    wf = Workflow()
    try:
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(config.CONSUMER_KEY, access_token)
        try:
            since = wf.cached_data('pocket_since', max_age=0)
            item_list = wf.cached_data('pocket_list', max_age=0)
            if not type(item_list) is list:
                item_list = []

            next_since = time()
            offset = 0
            while True:
                print offset
                state = 'all' if len(item_list) > 0 else None
                get = pocket_instance.get(sort='newest', detailType='complete', since=since, state=state, count=LINK_LIMIT, offset=offset)[0]

                if get['status'] != 1 or get['list'] == []:
                    break

                # Unpack and sort items
                for item in sorted(get['list'].values(), key=lambda x: int(x['time_added']), reverse=True):
                    if item['time_read'] == '0':
                        item_list.append(item)
                    else:
                        # Remove item
                        item_list[:] = [d for d in item_list if d.get('item_id') != item['item_id']]

                offset += LINK_LIMIT
                next_since = get['since']
                
            wf.cache_data('pocket_since', next_since)
            wf.cache_data('pocket_list', item_list)
            return item_list

        except AuthException:
            wf.cache_data('pocket_list', 'error1')
            wf.delete_password('pocket_access_token')
            wf.logger.error(
                'There was a problem receiving your Pocket list. The workflow has been deauthenticated automatically. Please try again!')
        # except Exception:
        #     wf.cache_data('pocket_list', 'error2')
        #     wf.logger.error(
        #         'Could not contact getpocket.com. Please check your Internet connection and try again!')

    except PasswordNotFound:
        wf.logger.error('Password not found!')

    return None


if __name__ == '__main__':
    refresh()
