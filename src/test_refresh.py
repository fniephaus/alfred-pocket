import unittest

import test_data
from pocket_api import AuthException, PocketException
from workflow import PasswordNotFound
import pocket_refresh
import pocket_refresh as pocket_refresh_backup

CachedData = {}
Passwords = {}


class PocketRefreshTestCase(unittest.TestCase):
    def test_exception_handling(self):
        def get(
            self,
            state=None,
            favorite=None,
            tag=None,
            contentType=None,
            sort=None,
            detailType=None,
            search=None,
            domain=None,
            since=None,
            count=None,
            offset=None,
        ):
            raise AuthException

        pocket_refresh.Pocket.get = get
        pocket_refresh.main()

        def get(
            self,
            state=None,
            favorite=None,
            tag=None,
            contentType=None,
            sort=None,
            detailType=None,
            search=None,
            domain=None,
            since=None,
            count=None,
            offset=None,
        ):
            raise PocketException

        pocket_refresh.Pocket.get = get
        pocket_refresh.main()

        def get_password(self, *args):
            raise PasswordNotFound

        pocket_refresh.Workflow.get_password = get_password
        pocket_refresh.main()

    def test_refresh(self):
        self.monkeypatch_refresh()
        pocket_refresh.main()
        self.assertTrue("1" in CachedData["pocket_list"])
        self.assertTrue("2" in CachedData["pocket_list"])
        self.assertTrue("300" in CachedData["pocket_list"])
        self.assertEqual(len(CachedData["pocket_list"]), 4)

        pocket_refresh.main()
        self.assertTrue("1" in CachedData["pocket_list"])
        self.assertTrue("2" in CachedData["pocket_list"])
        self.assertTrue("4" in CachedData["pocket_list"])
        self.assertTrue("300" in CachedData["pocket_list"])
        self.assertTrue("1337" in CachedData["pocket_list"])
        self.assertEqual(len(CachedData["pocket_list"]), 5)

    def monkeypatch_refresh(self):
        def get(
            self,
            state=None,
            favorite=None,
            tag=None,
            contentType=None,
            sort=None,
            detailType=None,
            search=None,
            domain=None,
            since=None,
            count=None,
            offset=None,
        ):
            if offset == 0:
                if CachedData == {}:
                    return [test_data.get_refresh_initial()]
                else:
                    return [test_data.get_refresh_delta(since)]
            return [test_data.get_refresh_end(since)]

        pocket_refresh.Pocket.get = get

        pocket_refresh.Workflow.get_password = lambda x, y: x

        def cached_data(self, key, max_age=None):
            return CachedData.get(key)

        pocket_refresh.Workflow.cached_data = cached_data

        def cache_data(self, key, data):
            CachedData[key] = data

        pocket_refresh.Workflow.cache_data = cache_data

    def setUp(self):
        pocket_refresh = pocket_refresh_backup
        CachedData.clear()
        Passwords.clear()

        def cached_data(self, key, max_age=None):
            pass

        def cache_data(self, key, data):
            pass

        pocket_refresh.Workflow.cached_data = cached_data
        pocket_refresh.Workflow.cache_data = cache_data

        def get_password(self, key):
            return Passwords.get(key)

        pocket_refresh.Workflow.get_password = get_password

        def delete_password(self, key):
            if key in Passwords:
                del Passwords[key]

        pocket_refresh.Workflow.delete_password = delete_password


if __name__ == "__main__":
    unittest.main()
