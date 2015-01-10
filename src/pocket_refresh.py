from time import time

from urllib2 import URLError
from pocket_api import Pocket, AuthException, PocketException
from workflow import Workflow, PasswordNotFound

import config

LINK_LIMIT = 2000

if __name__ == '__main__':
    wf = Workflow()
    error = None
    try:
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(config.CONSUMER_KEY, access_token)

        links = wf.cached_data('pocket_list', max_age=0)
        links = {}
        
        # only use delta syncing if dict is not empty
        if links:
            since = wf.cached_data('pocket_since', max_age=0)
        else:
            since = 0

        if not type(links) is dict:
            links = {}

        state = 'all' if links else None

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

            data = get['list']

            if get['status'] != 1 or data == []:
                break

            for item_id in data.keys():
                if data[item_id]['status'] == u'0':
                    links[item_id] = data[item_id]
                else:
                    # Remove item
                    del links[item_id]

        if next_since > since:
            wf.cache_data('pocket_since', next_since)
            wf.cache_data('pocket_list', links)

    except AuthException:
        error = 'AuthException'
        wf.cache_data('pocket_list', error)
        wf.delete_password('pocket_access_token')

    except (URLError, PocketException, PasswordNotFound), e:
        error = type(e).__name__
        wf.cache_data('pocket_list', error)

    if error:
        wf.logger.error(error)
