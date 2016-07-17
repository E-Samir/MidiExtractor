#!/usr/bin/env python
import fnmatch
import logging

import os
import uuid
from music21 import converter, instrument  # or import *


def recursive_mkdir(newdir):
    """works the way mkdir -p should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            recursive_mkdir(head)
        if tail:
            os.mkdir(newdir)


def get_output_folder(song):
    # base_path=os.path.dirname(song)
    song = os.path.basename(song)

    folder = "out/{}/tracks".format(os.path.splitext(song)[0])
    if not os.path.exists(folder):
        recursive_mkdir(folder)

    return os.path.join(folder, str(uuid.uuid1()) + ".mid")


def find_all_files(folder):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, '*.midi'):
            matches.append(os.path.join(root, filename))

    return matches

def split_song(song):
    s = converter.parse(song)
    for part in s.parts:
        out_name = get_output_folder(song)
        part.write('midi', fp=out_name)

def music_21():
    all_songs = find_all_files(os.path.realpath("../midiscraper/out/"))

    for song in all_songs:
        folder = os.path.dirname(get_output_folder(song))
        logging.debug("removing folder: {}".format(folder))
        os.system("rm -fr {}".format(folder))
        logging.debug("Splitting song: {}".format(song))
        import shutil
        parts = folder.split("/")
        parts = parts[:len(parts)-1]
        dest_song = "/".join(parts)
        shutil.copy(song, dest_song)
        split_song(song)


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    music_21()


if __name__ == '__main__':
    main()