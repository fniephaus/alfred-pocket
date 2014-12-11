from time import time

from urllib2 import URLError
from pocket import Pocket, AuthException, PocketException
from workflow import Workflow, PasswordNotFound

import config

LINK_LIMIT = 2000

if __name__ == '__main__':
    wf = Workflow()
    error = None
    try:
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(config.CONSUMER_KEY, access_token)

        item_list = wf.cached_data('pocket_list', max_age=0)
        
        # only use delta syncing if list is not empty
        if item_list and len(item_list) > 0:
            since = wf.cached_data('pocket_since', max_age=0)
        else:
            since = 0

        if not type(item_list) is list:
            item_list = []

        state = 'all' if len(item_list) > 0 else None

        next_since = 0
        offset = 0
        while True:
            get = pocket_instance.get(
                sort='newest',
                detailType='complete',
                since=since,
                state=state,
                count=LINK_LIMIT,
                offset=offset
            )[0]

            offset += LINK_LIMIT
            next_since = get['since']

            if get['status'] != 1 or get['list'] == []:
                break

            # Unpack and sort items
            for item in sorted(get['list'].values(), key=lambda x: int(x['item_id'])):
                if item['status'] == u'0':
                    item_list.append(item)
                else:
                    # Remove item
                    item_list[:] = [
                        d for d in item_list if d.get('item_id') != item['item_id']]

        if next_since > since:
            wf.cache_data('pocket_since', next_since)
            wf.cache_data('pocket_list', item_list)

    except AuthException:
        error = 'AuthException'
        wf.cache_data('pocket_list', error)
        wf.delete_password('pocket_access_token')

    except (URLError, PocketException, PasswordNotFound), e:
        error = type(e).__name__
        wf.cache_data('pocket_list', error)

    if error:
        wf.logger.error(error)
