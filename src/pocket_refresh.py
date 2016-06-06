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

        since = wf.cached_data('pocket_since', max_age=0) or 0
        links = wf.cached_data('pocket_list', max_age=0) or {}

        next_since = 0
        offset = 0
        while True:
            get = pocket_instance.get(
                detailType='complete',
                since=since,
                state='all',
                count=LINK_LIMIT,
                offset=offset
            )[0]

            data = get['list']
            next_since = get['since']

            if get['status'] != 1 or len(data) == 0:
                break

            links.update(data)
            offset += LINK_LIMIT

        # Delete obsolete entries
        for item_id in links.keys():
            if links[item_id]['status'] == '2':
                del links[item_id]

        wf.cache_data('pocket_since', next_since)
        wf.cache_data('pocket_list', links)
        tags = list(set([t for l in links.values() if 'tags' in l
                        for t in l['tags'].keys()]))
        wf.cache_data('pocket_tags', tags)

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


if __name__ == '__main__':
    main()  # pragma: no cover
