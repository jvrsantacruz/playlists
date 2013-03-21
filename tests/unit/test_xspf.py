#-*- coding: utf-8 -*-

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from hamcrest import *
from matchers import *

from playlists.lists import Xspf, XspfError

does_not = is_not


EMPTY_PL = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
  </trackList>
</playlist>
"""

TITLE = u'Braintrust'
PATH = u'/music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3'

ONE_TRACK_PL = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
  </trackList>
    <track>
      <title>Braintrust</title>
      <creator>Hot Snakes</creator>
      <album>Thunder Down Under</album>
      <duration>114000</duration>
      <location>file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3</location>
    </track>
  </playlist>
"""

MISSING_TITLE_PL = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
  </trackList>
    <track>
      <creator>Hot Snakes</creator>
      <album>Thunder Down Under</album>
      <duration>114000</duration>
      <location>file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3</location>
    </track>
  </playlist>
"""

SEVERAL_TRACKS_PL = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <trackList>
  </trackList>
    <track>
      <title>Braintrust</title>
      <creator>Hot Snakes</creator>
      <album>Thunder Down Under</album>
      <duration>114000</duration>
      <location>file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3</location>
    </track>
    <track>
      <title>Braintrust</title>
      <creator>Hot Snakes</creator>
      <album>Thunder Down Under</album>
      <duration>114000</duration>
      <location>file:///music/Hot_Snakes-Thunder_Down_Under-2006/01-hot_snakes-braintrust.mp3</location>
    </track>
  </playlist>
"""


class TestXspf(object):
    def test_ns_attribute_is_set(self):
        assert_that(Xspf.ns, is_not(none()))

    def test_parse_takes_file_like_objects(self):
        Xspf.parse(StringIO(u'<element/>'))

    def test_parse_raises_parse_error_on_empty_documents(self):
        with assert_that_raises(XspfError):
            list(Xspf.parse(StringIO()))

    def test_xspf_is_iterable(self):
        playlist = Xspf(StringIO(EMPTY_PL))

        assert_that(playlist, is_(iterable()))

    def test_parse_takes_empty_playlists(self):
        playlist = Xspf.parse(StringIO(EMPTY_PL))

        assert_that(playlist, is_(empty()))

    def test_parse_parses_playlists(self):
        playlist = Xspf.parse(StringIO(ONE_TRACK_PL))

        assert_that(playlist, has_len(1))

    def test_parse_retrieves_title_and_path(self):
        playlist = Xspf.parse(StringIO(ONE_TRACK_PL))

        assert_that(list(playlist), is_([(TITLE, PATH)]))

    def test_parse_retrieves_path_without_file_prefix(self):
        playlist = Xspf.parse(StringIO(ONE_TRACK_PL))

        track = list(playlist)[0]

        assert_that(track[1], does_not(starts_with('file://')))

    def test_parse_fills_missing_fields_with_none(self):
        playlist = Xspf.parse(StringIO(MISSING_TITLE_PL))

        track = list(playlist)[0]

        assert_that(track[0], is_(none()))

    def test_parse_parses_more_than_one_track(self):
        playlist = Xspf.parse(StringIO(SEVERAL_TRACKS_PL))

        assert_that(playlist, has_len(2))
