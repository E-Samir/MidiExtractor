#!/usr/bin/env python
import argparse
import fnmatch
import logging

import os
import uuid
from music21 import converter, instrument  # or import *
import shutil
import multiprocessing
from multiprocessing import Process, Queue
from lib.utils import recursive_mkdir, find_all_files


class MidiExtractor:
    queue = None

    def __init__(self, workers):
        self.queue = Queue()
        self.workers = int(workers)

        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    def get_output_folder(self, song):
        # base_path=os.path.dirname(song)
        song = os.path.basename(song)

        folder = "out/{}/tracks".format(os.path.splitext(song)[0])
        if not os.path.exists(folder):
            recursive_mkdir(folder)

        return os.path.join(folder, str(uuid.uuid1()) + ".mid")

    def __process_song__(self):
        while not self.queue.empty():
            song = self.queue.get()
            folder = os.path.dirname(self.get_output_folder(song))
            logging.debug("removing folder: {}".format(folder))
            os.system("rm -fr {}".format(folder))
            logging.debug("Splitting song: {}".format(song))
            parts = folder.split("/")
            parts = parts[:len(parts) - 1]
            dest_song = "/".join(parts)
            shutil.copy(song, dest_song)
            stream = converter.parse(song)
            for part in stream.parts:
                out_name = self.get_output_folder(song)
                part.write('midi', fp=out_name)

    def process_songs(self, input_data):
        all_songs = find_all_files(os.path.realpath(input_data), "*.midi")

        ##add all songs into queue
        for song in all_songs:
            self.queue.put(song)

        jobs = []
        for i in range(self.workers):
            p = multiprocessing.Process(target=self.__process_song__)
            jobs.append(p)
            p.start()


def main():
    parser = argparse.ArgumentParser(description='Midi Processor Script')
    parser.add_argument('--songdir', action="store", dest="songdir", default="all", help="override song")
    parser.add_argument('--workers', action="store", dest="workers", default="1", help="default workers")

    args = parser.parse_args()

    foobar = MidiExtractor(args.workers)
    if args.songdir == 'all':
        foobar.process_songs("../midiscraper/out/")
    else:
        foobar.process_songs(args.songdir)


if __name__ == '__main__':
    main()
