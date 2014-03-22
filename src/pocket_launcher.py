import sys
import os
import json
from pocket import Pocket
from workflow import Workflow

CONSUMER_KEY = '25349-924436f8cc1abc8370f02d9d'


def execute(wf):
    query = json.loads(''.join(wf.args))
    if 'item_id' in query:
        access_token = wf.get_password('pocket_access_token')
        pocket_instance = Pocket(CONSUMER_KEY, access_token)
        pocket_instance.archive(query['item_id'], wait=False)

    if 'url' in query:
        os.system('open %s' % query['url'])


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(execute))
