import unittest
import logging
import sys

import pocket
import pocket as pocket_backup

import test_data

CachedData = {}
Passwords = {}


class PocketTestCase(unittest.TestCase):

    def test_main(self):
        CachedData['__workflow_update_status'] = {
            'available': True
        }
        CachedData['pocket_list'] = test_data.get_normal()
        sys.argv = ['pocket.py', '']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.main(None)

    def test_main_error(self):
        CachedData['__workflow_update_status'] = {
            'available': True
        }
        CachedData['pocket_error'] = 'AuthException'
        sys.argv = ['pocket.py', '']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.main(None)

    def test_main_empty(self):
        CachedData['__workflow_update_status'] = {
            'available': True
        }
        sys.argv = ['pocket.py', '']

        def send_feedback():
            pass
        pocket.WF.send_feedback = send_feedback
        pocket.main(None)

    def test_register_magic_arguments(self):
        pocket.WF = pocket.Workflow()
        self.assertTrue('deauth' not in pocket.WF.magic_arguments)
        pocket.register_magic_arguments()
        pocket.WF.magic_arguments['deauth']()
        self.assertTrue('deauth' in pocket.WF.magic_arguments)
        self.assertEquals(pocket.WF.magic_prefix, 'wf:')

    def test_get_links(self):
        def cached_data(self, key, max_age=None):
            if 'pocket_list' not in CachedData:
                CachedData['pocket_list'] = 12345
                return None
            return CachedData.get(key)
        pocket.Workflow.cached_data = cached_data
        self.assertEquals(pocket.get_links(), 12345)

        CachedData.clear()
        self.assertEquals(pocket.get_links(tries=0), {})

    def test_add_items(self):
        self.assertEquals(len(pocket.WF._items), 0)
        pocket.add_items(links={}, user_input='')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, 'No links found for "".')

        pocket.WF._items = []
        pocket.add_items(links={'1': {
            'item_id': '1',
            'given_title': 'test',
            'given_url': 'url',
            'time_updated': '10',
        }}, user_input='')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, 'test')

        pocket.WF._items = []
        pocket.add_items(links={'1': {
            'item_id': '1',
            'given_title': 'test',
            'resolved_title': 'test',
            'given_url': 'url',
            'time_updated': '10',
            'tags': {'alfred': {'item_id': '4444', 'tag': 'alfred'}}
        }}, user_input='notfound')
        self.assertEquals(len(pocket.WF._items), 1)
        self.assertEquals(pocket.WF._items[0].title, "No links found for "
                                                     "\"notfound\".")

    def test_get_auth_url(self):
        expected_start = 'https://getpocket.com/auth/authorize?'
        self.assertTrue(pocket.get_auth_url().startswith(expected_start))

    def setUp(self):
        pocket = pocket_backup
        CachedData.clear()
        Passwords.clear()

        pocket.Workflow.alfred_env = {
            'theme_background': 'rgba(40,40,40,0.1)',
        }

        logging.disable(logging.CRITICAL)

        def cached_data(self, key, max_age=None):
            return CachedData.get(key)
        pocket.Workflow.cached_data = cached_data

        def cache_data(self, key, data):
            CachedData[key] = data
        pocket.Workflow.cache_data = cache_data

        def get_password(self, key):
            return Passwords.get(key)
        pocket.Workflow.get_password = get_password

        def delete_password(self, key):
            if key in Passwords:
                del Passwords[key]
        pocket.Workflow.delete_password = delete_password

        def refresh_list():
            pass
        pocket.refresh_list = refresh_list


if __name__ == "__main__":
    unittest.main()
