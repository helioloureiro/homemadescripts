#! /usr/bin/python3

"""
Handling GPG signing keys, sending automated info to destinations.
"""
import sys

class SigningTool:
    def __init__(self):
        None
        self.keys = []

    def get_ids(self, keys = []):
        """
        Read key(s) from stdin.
        """
        if not keys:
            if len(sys.argv) < 2:
                raise RuntimeError("missing arguments")
            else:
                self.keys = sys.argv[1:]
        else:
            self.keys = keys

    def run(self, keys=[]):
        self.get_ids(keys)

if __name__ == '__main__':
    s = SigningTool()
    s.run()
