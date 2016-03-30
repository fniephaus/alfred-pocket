def get_normal():
    return {
        u'http://google.com': {
            u'excerpt': u'abc123',
            u'favorite': u'0',
            u'given_title': u'',
            u'given_url': u'http://google.com',
            u'has_image': u'1',
            u'is_article': u'0',
            u'is_index': u'1',
            u'item_id': u'1111',
            u'resolved_id': u'1111',
            u'resolved_title': u'',
            u'resolved_url': u'',
            u'status': u'0',
            u'time_added': u'54321',
            u'time_favorited': u'0',
            u'time_updated': u'54321',
        },
        u'http://fniephaus.com': {
            u'excerpt': u'abc',
            u'favorite': u'0',
            u'given_title': u'',
            u'given_url': u'http://fniephaus.com',
            u'has_image': u'0',
            u'is_article': u'1',
            u'is_index': u'0',
            u'item_id': u'2222',
            u'resolved_id': u'2222',
            u'resolved_title': u'',
            u'resolved_url': u'',
            u'status': u'0',
            u'time_added': u'1396054841',
            u'time_favorited': u'0',
            u'time_updated': u'1396054841',
        },
        u'http://github.com': {
            u'excerpt': u'text2',
            u'favorite': u'0',
            u'given_title': u'title321',
            u'given_url': u'http://github.com',
            u'has_image': u'1',
            u'is_article': u'0',
            u'is_index': u'0',
            u'item_id': u'3333',
            u'resolved_id': u'722186783',
            u'resolved_title': u'resolvedtitle',
            u'resolved_url': u'',
            u'status': u'0',
            u'time_added': u'1411528927',
            u'time_favorited': u'0',
            u'time_updated': u'1411528927',
            u'videos': {},
        }
    }


def get_refresh_initial():
    return {
        u'status': 1,
        u'error': None,
        u'complete': 1,
        u'since': 1,
        u'list': get_normal()
    }


def get_refresh_delta(since):
    return {
        u'status': 1,
        u'error': None,
        u'complete': 0,
        u'since': since + 10,
        u'list': {
            u'http://nasa.gov': {
                u'status': u'0',
                u'is_index': u'0',
                u'time_updated': u'1420711247',
                u'time_favorited': u'0',
                u'excerpt': u'',
                u'has_image': u'0',
                u'favorite': u'0',
                u'given_title': u'title123',
                u'resolved_url': u'',
                u'is_article': u'0',
                u'item_id': u'4444',
                u'time_added': u'1420711246',
                u'resolved_id': u'4444',
                u'given_url': u'http://nasa.gov',
                u'resolved_title': u''
            },
            u'http://github.com': {
                u'status': u'1',
                u'is_index': u'0',
                u'time_updated': u'1420892898',
                u'time_favorited': u'0',
                u'excerpt': u"ec",
                u'has_image': u'1',
                u'favorite': u'0',
                u'given_title': u'',
                u'resolved_url': u'',
                u'is_article': u'1',
                u'item_id': u'1111',
                u'time_added': u'1420828162',
                u'resolved_id': u'1111',
                u'given_url': u'http://github.com',
                u'resolved_title': u''
            }
        }
    }


def get_refresh_end(since):
    return {
        u'status': 0,
        u'error': None,
        u'complete': 0,
        u'since': since + 10,
        u'list': {}
    }
