#-*- coding: utf-8 -*-

import os
from lxml import objectify


class PIterable(object):
    "Base class for iterable playlists"

    def __init__(self, path):
        "Base constructor, sets self.path"
        self.path = path

    def __iter__(self):
        "Returns a new object to iterate with it"
        klass = type(self)
        return klass(self.path)


class Xspf(PIterable):
    "Iterate over a XSPF playlist file."

    ns = "http://xspf.org/ns/0/"

    def __init__(self, path):
        super(Xspf, self).__init__(path)
        self.root = objectify.parse(path).getroot()
        self.list = self.root.trackList.track[:]
        self.index = 0

    def next(self):
        "Returns title, absolute_path for every item on the list"
        if self.index == len(self.list):
            raise StopIteration

        # get title and remove initial file:///
        title = self.list[self.index].title.text.encode('utf-8')
        path = self.list[self.index].location.text.encode('utf-8')[7:]

        self.index += 1  # next track

        return title, path


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
