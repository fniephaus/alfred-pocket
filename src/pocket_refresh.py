from time import time

from urllib2 import URLError
from pocket_api import Pocket, AuthException, PocketException
from workflow import Workflow, PasswordNotFound

import config

LINK_LIMIT = 2000


def main():
    wf = Workflow()
    error = None
    try:
        # initialize client
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(config.CONSUMER_KEY, access_token)

        state = None
        since = wf.cached_data('pocket_since', max_age=0) or 0
        links = {}
        # fetch cached links if since is not 0
        if since > 0:
            links = wf.cached_data('pocket_list', max_age=0) or {}
            
            # Only use delta syncing if dict is not empty
            if links:
                state = 'all'

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

            data = get['list']
            next_since = get['since']

            if get['status'] != 1 or len(data) == 0:
                break

            links = sync_data(links, data)
            offset += LINK_LIMIT

        wf.cache_data('pocket_since', next_since)
        wf.cache_data('pocket_list', links)

    except (AuthException, URLError, PocketException, PasswordNotFound), e:
        error = type(e).__name__
        wf.cache_data('pocket_error', error)

        # delete token if authentication failed
        if error == 'AuthException':
            wf.delete_password('pocket_access_token')

    if error:
        wf.logger.error(error)
    else:
        # delete error file if it exists
        wf.cache_data('pocket_error', None)


def sync_data(links, data):
    for item_id in data.keys():
        if data[item_id]['status'] == u'0':
            # Add item
            links[item_id] = data[item_id]
        elif item_id in links:
            # Remove item
            del links[item_id]
    return links

if __name__ == '__main__':
    main() # pragma: no cover
