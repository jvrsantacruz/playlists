#-*- coding: utf-8 -*-

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from hamcrest import *
from matchers import *

from playlists import Asx, AsxError

does_not = is_not

EMPTY_PL = """<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
</asx>
"""

TITLE = u'Braintrust'
PATH = u'/music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3'

ONE_TRACK_PL = """<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
    <entry>
        <title>Braintrust</title>
        <ref href="file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3"/>
        <author>Hot Snakes</author>
    </entry>
</asx>
"""

MISSING_TITLE_PL = """<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
    <entry>
        <ref href="file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3"/>
        <author>Hot Snakes</author>
    </entry>
</asx>
"""

SEVERAL_TRACKS_PL = """<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
    <entry>
        <title>Braintrust</title>
        <ref href="file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3"/>
        <author>Hot Snakes</author>
    </entry>
    <entry>
        <title>Hi-Lites</title>
        <ref href="file:///music/Hot_Snakes-Thunder_Down_Under-2006-SDR/02-hot_snakes-hi-lites.mp3"/>
        <author>Hot Snakes</author>
    </entry>
</asx>
"""


class TestAsx(object):
    def test_ns_attribute_is_set(self):
        assert_that(Asx.ns, is_not(none()))

    def test_parse_takes_file_like_objects(self):
        Asx.parse(StringIO(u'<element/>'))

    def test_parse_raises_parse_error_on_empty_documents(self):
        with assert_that_raises(AsxError):
            list(Asx.parse(StringIO()))

    def test_xspf_is_iterable(self):
        playlist = Asx(StringIO(EMPTY_PL))

        assert_that(playlist, is_(iterable()))

    def test_parse_takes_empty_playlists(self):
        playlist = Asx.parse(StringIO(EMPTY_PL))

        assert_that(playlist, is_(empty()))

    def test_parse_parses_playlists(self):
        playlist = Asx.parse(StringIO(ONE_TRACK_PL))

        assert_that(playlist, has_len(1))

    def test_parse_retrieves_title_and_path(self):
        playlist = Asx.parse(StringIO(ONE_TRACK_PL))

        assert_that(list(playlist), is_([(TITLE, PATH)]))

    def test_parse_retrieves_path_without_file_prefix(self):
        playlist = Asx.parse(StringIO(ONE_TRACK_PL))

        track = list(playlist)[0]

        assert_that(track[1], does_not(starts_with('file://')))

    def test_parse_fills_missing_fields_with_none(self):
        playlist = Asx.parse(StringIO(MISSING_TITLE_PL))

        track = list(playlist)[0]

        assert_that(track[0], is_(none()))

    def test_parse_parses_more_than_one_track(self):
        playlist = Asx.parse(StringIO(SEVERAL_TRACKS_PL))

        assert_that(playlist, has_len(2))
