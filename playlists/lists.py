#-*- coding: utf-8 -*-

import os

from xml.etree.ElementTree import iterparse, ParseError


class PIterable(object):
    "Base class for iterable playlists"

    def __init__(self, path):
        "Base constructor, sets self.path"
        self.path = path

    def __iter__(self):
        "Returns a new object to iterate with it"
        klass = type(self)
        return klass(self.path)


class PlaylistError(Exception):
    pass


class XspfError(Exception):
    pass


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

                if element.tag.endswith('track'):
                    yield title, location

                    # Clean after reading a track
                    title, location = None, None
                    root.clear()

        except ParseError as error:
            raise XspfError(error)


class M3u(PIterable):
    "Iterate over a M3U playlist file."

    ns = "#EXTM3U"

    def __init__(self, path):
        super(M3u, self).__init__(path)
        self.base_path = os.path.dirname(self.path)
        self.file = open(self.path, "r")

    def next(self):
        """Returns title, absolute_path for every item on the playlist.

        M3u objects have the following structure:

        #EXTM3U
        #EXTINF:342,Author - Song Title
        ../Music/song.mp3
        """

        # Find a #EXTINF line and a path line
        line, line_prev = '#', ''
        while line.startswith('#'):
            line_prev = line
            line = self.file.readline()
            if not line:
                raise StopIteration

        title = line_prev.split(',', 1)[1]  # get title
        path = os.path.join(self.base_path, line)[0:-1]

        return title, path
