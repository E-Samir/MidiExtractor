#!/usr/bin/env python
import argparse
import fnmatch
import logging

import os
import uuid
from music21 import converter, instrument  # or import *
import shutil


class MidiExtractor:
    def __init__(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    def __recursive_mkdir__(self, newdir):
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
                self.__recursive_mkdir__(head)
            if tail:
                os.mkdir(newdir)

    @staticmethod
    def find_all_files(folder, pattern):
        matches = []
        for root, dirnames, filenames in os.walk(folder):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))

        return matches

    def get_output_folder(self, song):
        # base_path=os.path.dirname(song)
        song = os.path.basename(song)

        folder = "out/{}/tracks".format(os.path.splitext(song)[0])
        if not os.path.exists(folder):
            self.__recursive_mkdir__(folder)

        return os.path.join(folder, str(uuid.uuid1()) + ".mid")

    def split_song(self, song):
        s = converter.parse(song)
        for part in s.parts:
            out_name = self.get_output_folder(song)
            part.write('midi', fp=out_name)

    def process_songs(self, input_data):
        all_songs = self.find_all_files(os.path.realpath(input_data), "*.midi")

        for song in all_songs:
            folder = os.path.dirname(self.get_output_folder(song))
            logging.debug("removing folder: {}".format(folder))
            os.system("rm -fr {}".format(folder))
            logging.debug("Splitting song: {}".format(song))
            parts = folder.split("/")
            parts = parts[:len(parts) - 1]
            dest_song = "/".join(parts)
            shutil.copy(song, dest_song)
            self.split_song(song)


def main():
    parser = argparse.ArgumentParser(description='Midi Processor Script')
    parser.add_argument('--songdir', action="store", dest="songdir", default="all", help="override song")

    args = parser.parse_args()

    foobar = MidiExtractor()
    if args.songdir == 'all':
        foobar.process_songs("../midiscraper/out/")
    else:
        foobar.process_songs(args.songdir)


if __name__ == '__main__':
    main()
