# Playlist 

Multi-format music playlist file exporter. 

Copies the files from a playlist.

# Export playlist to files

Using the command `playlists` a playlist can be exported into actual files with no need for pick them one by one.


```bash
playlists rock-and-roll.m3u  /media/mp3player/MUSIC
```

# Installation

```bash 
python setup.py install
```

# Requirements

Just `python2.7`

# Development

virtualenv + develop + run tests

``bash
mkvirtualenv playlists --python python2 --distribute
workon playlists

python setup.py develop
pip install -r dev-reqs.txt

nosetests
```
