#-*- coding: utf-8 -*-

from xml.etree.ElementTree import iterparse, ParseError


class Asx(object):
    "Iterate over a Asx playlist file."

    ns = '<asx version="3.0">'

    def __init__(self, source):
        self.source = source

    def __iter__(self):
        return self.parse(self.source)

    @staticmethod
    def parse(source):
        """Yields title, absolute_path for every item on the list

        asx documents have the following structure:

        <asx version="3.0">
            <entry>
                <title>Braintrust</title>
                <ref href="file:///music/Hot_Snakes-Thunder_Down_Under-2006-SDR/01-hot_snakes-braintrust.mp3"/>
                <author>Hot Snakes</author>
            </entry>
        </asx>
        """
        document = iterparse(source, events=('start', 'end'))

        def get_root(document):
            for event, element in document:
                return element

        try:
            title, location = None, None
            root = get_root(document)
            end_events = (el for event, el in document if event == 'end')

            for element in end_events:
                if element.tag.endswith('title'):
                    title = element.text

                elif element.tag.endswith('ref'):
                    location = element.get('href')
                    if location is not None:
                        location = location[7:]

                elif element.tag.endswith('entry'):
                    yield title, location

                    # Clean after reading a track
                    title, location = None, None
                    root.clear()

        except ParseError as error:
            raise AsxError(error)


class Xspf(object):
    "Iterate over a XSPF playlist file."

    ns = "http://xspf.org/ns/0/"

    def __init__(self, source):
        self.source = source

    def __iter__(self):
        return self.parse(self.source)

    @staticmethod
    def parse(source):
        """Yields title, absolute_path for every item on the list

        xspf documents have the following structure:

    <?xml version="1.0" encoding="UTF-8"?>
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
        document = iterparse(source, events=('start', 'end'))

        def get_root(document):
            for event, element in document:
                return element

        try:
            title, location = None, None
            root = get_root(document)
            end_events = (el for event, el in document if event == 'end')

            for element in end_events:
                if element.tag.endswith('title'):
                    title = element.text

                elif element.tag.endswith('location'):
                    location = element.text[7:]

                elif element.tag.endswith('track'):
                    yield title, location

                    # Clean after reading a track
                    title, location = None, None
                    root.clear()

        except ParseError as error:
            raise XspfError(error)


class M3u(object):
    "Iterate over a M3U playlist file."

    ns = "#EXTM3U"

    def __init__(self, source):
        self.source = source

    def __iter__(self):
        return self.parse(self.source)

    @staticmethod
    def parse(source):
        """Yields title, absolute_path for every item on the playlist.

        M3u files have the following structure:

        #EXTM3U
        #EXTINF:342,Author - Song Title
        ../Music/song.mp3
        """
        content_lines = (line for line in source if line)

        def get_first_line(source):
            for line in content_lines:
                return line

        first_line = get_first_line(source)
        if not first_line or not first_line.startswith('#EXTM3U'):
            raise M3uError(u'playlist does not start with #EXTM3U')

        title, path = None, None
        for line in content_lines:
            if line.startswith('#EXTINF'):
                title = line.split(',', 1)[1][:-1]  # remove zn
            else:
                path = line[:-1]  # remove \n

            if title and path:
                yield title, path
                title, path = None, None  # clean after reading a track


class PlaylistError(Exception):
    pass


class XspfError(Exception):
    pass


class AsxError(Exception):
    pass


class M3uError(Exception):
    pass
