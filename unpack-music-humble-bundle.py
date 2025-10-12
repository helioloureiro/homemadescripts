#! /usr/bin/env python3

import os
import sys
import argparse
import re
import subprocess


def shellExec(command: str) -> str:
    'https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running'
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)

class UnPacker:
    'A class to handle Humble Bundle music'

    _directory : str = None

    def __init__(self):
        parser = argparse.ArgumentParser(description="A script to unpack the music pack from Humble Bundle and convert the audio from wav to mp3")
        parser.add_argument("--directory", help="The directory to parse, otherwise use the current directory.")
        args = parser.parse_args()

        if args.directory:
            self._directory = args.directory


    def run(self):
        if self._directory is None:
            current_dir = os.path.dirname(".")
            self._directory = current_dir
            print(f"📂 reading from directory: {current_dir}")

        os.chdir(self._directory)

        files_available = self.get_directory_listing()
        print(f"📄 available files: {files_available}")
        for filename in files_available:
            self.unzip(filename)

        for (path, _, filenames) in os.walk(self._directory):
            print(f"Processing: {path}")
            os.chdir(path)
            for filename in filenames:
                  self.convert_waves(filename)
   


    def get_directory_listing(self, directory=None) -> list[str]:
        listing = list()
        if directory is None:
            directory = "."
        listing = os.listdir(directory)
        return sorted(listing)

    def unzip(self, filename):
        if not re.search(r"\.zip$", filename):
            return
        print(f"🗜️ uncompressing: {filename}")
        for line in shellExec(["unzip", filename]):
            print(line, end="")

    def convert_waves(self, filename):
        print(f"Checking: {filename}")
        if os.path.isdir(filename):
            print(f"📂 getting into directory: {filename}")
            os.chdir(filename)
            files_available = self.get_directory_listing()
            for inner_filename in files_available:
                self.convert_waves(inner_filename)
        else:
            is_dir = os.path.isdir(filename)
            cur_dir = os.path.abspath(os.curdir)
            if not re.search(r"\.wav$", filename):
                print(f"❎ skipping file: {filename} - is a dir? {is_dir} - current directory: {cur_dir}")
                return
            print(f"♫ converting: {filename}")
            filename_root = os.path.basename(filename)
            filename_root = re.sub(r"\.wav", "", filename_root)
            if os.path.exists(f"{filename_root}.mp3"):
                print(f"{filename_root}.mp3 was already generated")
                return
            for line in shellExec(["ffmpeg", "-loglevel", "quiet", "-i", filename, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", f"{filename_root}.mp3"]):
                print(line, end="")

if __name__ == '__main__':
    up = UnPacker()
    up.run()
