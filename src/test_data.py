def get_normal():
    return {
        u'1111': {
            u'status': u'0',
            u'is_index': u'1',
            u'time_updated': u'54321',
            u'time_favorited': u'0',
            u'excerpt': u'abc123',
            u'has_image': u'1',
            u'favorite': u'0',
            u'given_title': u'',
            u'resolved_url': u'',
            u'is_article': u'0',
            u'item_id': u'1111',
            u'time_added': u'54321',
            u'resolved_id': u'1111',
            u'given_url': u'',
            u'resolved_title': u''
        },
        u'2222': {
            u'status': u'0',
            u'is_index': u'0',
            u'time_updated': u'1396054841',
            u'time_favorited': u'0',
            u'excerpt': u'abc',
            u'has_image': u'0',
            u'favorite': u'0',
            u'given_title': u'',
            u'resolved_url': u'',
            u'is_article': u'1',
            u'item_id': u'2222',
            u'time_added': u'1396054841',
            u'resolved_id': u'2222',
            u'given_url': u'',
            u'resolved_title': u''
        },
        u'3333': {
            u'videos': {},
            u'is_article': u'0',
            u'excerpt': u'text2',
            u'time_added': u'1411528927',
            u'status': u'0',
            u'resolved_url': u'',
            u'item_id': u'3333',
            u'resolved_id': u'722186783',
            u'given_url': u'',
            u'resolved_title': u'resolvedtitle',
            u'is_index': u'0',
            u'time_updated': u'1411528927',
            u'time_favorited': u'0',
            u'favorite': u'0',
            u'given_title': u'title321',
            u'has_image': u'1'
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
            u'4444': {
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
                u'given_url': u'',
                u'resolved_title': u''
            },
            u'1111': {
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
                u'given_url': u'',
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