#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Copy files listed in a playlist to a directory.

Javier Santacruz 04/06/2011
"""

import os
import shutil
import random
from optparse import OptionParser

from lists import Xspf, M3u


FORMATS = {"m3u": M3u, "xspf": Xspf}


def detect_format(source):
    """Autodetects the format of a playlist file
    returns (m3u|xspf) or None if unkown
    """
    header = source.readline(200)
    source.seek(0)  # reset source

    for name, cls in FORMATS.items():
        if cls.ns in header:
            return name


def get_playlist(path, format_name=None):
    """Returns a Playlist object of the given format.
    if format_name is not specified or None, format will be auto detected
    """
    try:
        source = open(path, 'r')
    except IOError as err:
        print(u"Error: Couldn't open playlist from '{}': {}".format(path, err))
        exit(1)

    if format_name is None:
        format_name = detect_format(source)

    if format_name is None:
        print(u"Error: Couldn't autodetect format for playlist.")
        exit(1)

    if format_name not in FORMATS:
        print(u"Error: Unkown '{}' playlist format.".format(format_name))
        exit(1)

    return FORMATS[format_name](source)


def prefix_name(number, name, total):
    """Returns name prefixed with number. Filled with zeros to fit total
    >>> prefix_name(15, 'filename', 3)
    '015_filename'
    >>> prefix_name(15, 'filename', 1)
    '15_filename'
    """
    return u"{num}_{name}".format(
        num=str(number).zfill(len(str(total))), name=name)


def get_expected_names(local_files):
    "Returns the filenames expected to be on remote"
    return [prefix_name(i + 1, name, len(local_files))
            for i, name in enumerate(local_files)]


def get_copy_names(local_files, expected_names, remote_names):
    "Returns the files to be copied"
    return [name for i, name in enumerate(local_files)
            if expected_names[i] not in remote_names]


def delete_files(expected_names, remote_dir):
    """Deletes files in remote which aren't expected to be there
    Returns the name of files effectively deleted
    """
    delete_list = [os.path.join(remote_dir, name)
                   for name in os.listdir(remote_dir)
                   if name not in expected_names]

    print(u"Removing {} files from '{}'".format(len(delete_list), remote_dir))

    deleted = 0
    for fpath in delete_list:
        try:
            os.remove(fpath)
        except OSError as err:
            print(u"Error: Couldn't remove '{}' from '{}': {}"
                  .format(os.path.basename(fpath), remote_dir, err))
        else:
            deleted += 1
            print(u"Removed {}/{}: {}".format(deleted, len(delete_list), fpath))

    return deleted


def link(from_path, to_path):
    "Wrapper around os.link. Returns True/False on success/failure"
    try:
        os.link(from_path, to_path)
    except OSError as err:
        print(u"Error: Couldn't link '{}' from '{}' to '{}': {}"
              .format(os.path.basename(from_path),
                      os.path.dirname(from_path),
                      to_path,
                      err))
        return False
    else:
        return True


def copy(from_path, to_path):
    "Wrapper around shutil.copy. Returns True/False on success/failure"
    try:
        shutil.copy(from_path, to_path)
    except shutil.Error as err:
        print (u"Error: Couldn't copy '{}' from '{}' to '{}': {}"
               .format(os.path.basename(from_path),
                       os.path.dirname(from_path),
                       to_path,
                       err))
        return False

    except IOError as err:
        print (u"Error: Couldn't copy '{}' from '{}' to '{}': {}"
               .format(os.path.basename(from_path), os.path.dirname(from_path),
                       to_path, err))
        return False

    return True


def send_files(copy_files, expected_names, remote_dir, dolink=False, force=False):
    """Copies/Links files to remote dir as expected_name
    Links instead of copying the files if link is True
    returns the number of files copied/linked
    """
    action = u"Linking" if dolink else u"Copying"
    print(u"{} {} files to '{}'".format(action, len(copy_files), remote_dir))

    copied = 0
    action = u"Linked" if dolink else u"Copied"
    for i, cfile in enumerate(copy_files):

        dest = os.path.join(remote_dir, expected_names[i])
        if not force and os.path.exists(dest):
            continue

        op_result = link(cfile, dest) if dolink else copy(cfile, dest)
        if op_result:
            copied += 1
            print(u"{} {}/{}: '{}'".format(action, copied, len(copy_files), cfile))

    return copied


def sync_dirs(local_files, remote_dir, opts):
    """Copy a set files to a directory.
    If delete is set, will remove files in remote which are not in local.
    If link is set, will perform hard link instead of copy.
    If force is set, will copy all files ignoring if they're already in remote.
    """
    if opts.cd:
        # Maximize de number of files in the CD
        # remove files from the playlist until it fits into a cd
        weighted_files = [(os.path.getsize(f) * 5, f) for f in local_files]
        weighted_files.sort(key=lambda item: item[0])  # small first
        total_size = sum(size for size, f in weighted_files)

        cdsize = 700 * 1024 * 1024  # in bytes
        while total_size > cdsize:
            size, f = weighted_files.pop()
            print(u"Ommiting '{}' to fit CD size".format(f))
            local_files.remove(f)
            total_size -= size

    # Obtain file names in order to compare file subsets
    if opts.shuffle:
        random.shuffle(local_files)

    local_names = [os.path.basename(f) for f in local_files]  # local names
    expected_names = local_names if not opts.numbered else get_expected_names(local_names)  # what sould be in remote
    remote_names = os.listdir(remote_dir)  # what is in remote

    # Remove undesired files
    deleted = 0
    if opts.delete:
        deleted = delete_files(expected_names, remote_dir)

    # Paths to be copied to remote
    copy_files = local_files if opts.force else get_copy_names(local_files, expected_names, remote_names)

    # Warn about already present files which are being skipped
    if not opts.force:
        for path in set(remote_names).intersection(set(expected_names)):
            print(u"Skipping '{}' which is already in '{}'"
                  .format(os.path.basename(path), remote_dir))

    # Copy/Link files to remote directory
    copied = send_files(copy_files, expected_names, remote_dir, opts.link, opts.force)
    action = u"Linking" if opts.link else u"Copying"

    print(u"{} complete: {} files copied, {} files removed"
          .format(action, copied, deleted))


def main(options, args, parser):

    pl_path = args[0]
    remote_dir = args[1]

    if options.nocreate and not os.path.exists(remote_dir):
        print(u"Error: {} doesn't exists.".format(remote_dir))
        exit()

    if not options.nocreate and not os.path.exists(remote_dir):
        try:
            os.mkdir(remote_dir)
        except OSError:
            print(u"Error: {} doesn't exists and couldn't be created."
                  .format(remote_dir))
            exit()

    if not os.path.isdir(remote_dir):
        print(u"Error: {} doesn't exists or is not a directory."
              .format(remote_dir))
        exit()

    playlist = get_playlist(pl_path, options.format)
    files = [os.path.realpath(f[1]) for f in playlist]

    sync_dirs(files, remote_dir, options)


def check_arguments(options, args, parser):
    # Check arguments
    errors = (("Error: Missing playlist and directory paths."),
              ("Error: Missing directory paths."),
              ("Error: Too many arguments."))

    if len(args) != 2:
        print(errors[len(args) if len(args) < 3 else 2] + u'\n')
        print(parser.print_help())
        exit(1)

    if options.mix:
        options.numbered = True
        options.shuffle = True

    if not os.path.isfile(args[0]):
        print("Error: playlist doesn't exist or isn't a file: {}. Exiting."
              .format(args[0]))
        exit(1)

    return options, args, parser


def parse_arguments():
    parser = OptionParser()

    parser.add_option("-d", "--delete", dest="delete",
                      action="store_true", default=False,
                      help="Delete files which are not in the playlist.")

    parser.add_option("-f", "--force", dest="force",
                      action="store_true", default=False,
                      help="Force copy. Doesn't skip already existing files.")

    parser.add_option("-l", "--link", dest="link",
                      action="store_true", default=False,
                      help="Hard linking instead of copying files.")

    parser.add_option("-c", "--nocreate", dest="nocreate",
                      action="store_true", default=False,
                      help="Doesn't create remote directory if doesn't exists")

    parser.add_option("-s", "--shuffle", dest="shuffle",
                      action="store_true", default=False,
                      help="Process files in a random order. Useful with"
                      "--numbered.")

    parser.add_option("-n", "--numbered", dest="numbered",
                      action="store_true", default=False,
                      help="Rename files using positional indicator i_name")

    parser.add_option("-m", "--mix", dest="mix",
                      action="store_true", default=False,
                      help="Like --shuffle --numbered")

    parser.add_option("-7", "--cd", dest="cd",
                      action="store_true", default=False,
                      help="Limits the list size to 700MiB")

    parser.add_option("-t", "--format", dest="format",
                      action="store", default=None,
                      help="Select format (m3u|xspf). Autodetects by default.")

    parser.set_usage("Usage: [options] playlist directory")

    options, args = parser.parse_args()

    return options, args, parser


if __name__ == "__main__":
    main(*check_arguments(*parse_arguments()))
