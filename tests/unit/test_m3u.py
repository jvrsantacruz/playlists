#-*- coding: utf-8 -*-

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from hamcrest import *
from matchers import *

from playlists import M3u, M3uError


EMPTY_PL = u"#EXTM3U"

TITLE = u'Hot Snakes - Braintrust'
PATH = u'/music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3'

ONE_TRACK_PL = """#EXTM3U
#EXTINF:114,Hot Snakes - Braintrust
/music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3
"""

SEVERAL_TRACKS_PL = """#EXTM3U
#EXTINF:152,Hot Snakes - Hi-Lites
/music/Hot_Snakes-Thunder_Down_Under-2006/02-hot_snakes-hi-lites.mp3
#EXTINF:172,Hot Snakes - Retrofit
/music/Hot_Snakes-Thunder_Down_Under-2006/03-hot_snakes-retrofit.mp3
"""


class TestM3u(object):
    def test_ns_attribute_is_set(self):
        assert_that(M3u.ns, is_not(none()))

    def test_parse_takes_file_like_objects(self):
        list(M3u.parse(StringIO(EMPTY_PL)))

    def test_parse_raises_parse_error_on_empty_sources(self):
        with assert_that_raises(M3uError):
            list(M3u.parse(StringIO()))

    def test_parse_raises_parse_error_on_wrong_headers(self):
        with assert_that_raises(M3uError):
            list(M3u.parse(StringIO('foo')))

    def test_playlist_is_iterable(self):
        playlist = M3u(StringIO(EMPTY_PL))

        assert_that(playlist, is_(iterable()))

    def test_parse_takes_empty_playlists(self):
        playlist = M3u.parse(StringIO(EMPTY_PL))

        assert_that(playlist, is_(empty()))

    def test_parse_parses_playlists(self):
        playlist = M3u.parse(StringIO(ONE_TRACK_PL))

        assert_that(playlist, has_len(1))

    def test_parse_retrieves_title_and_path(self):
        playlist = M3u.parse(StringIO(ONE_TRACK_PL))

        assert_that(list(playlist), is_([(TITLE, PATH)]))

    def test_parse_parses_more_than_one_track(self):
        playlist = M3u.parse(StringIO(SEVERAL_TRACKS_PL))

        assert_that(playlist, has_len(2))
