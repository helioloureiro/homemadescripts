#! /usr/bin/python3

import time
import hashlib
import os

SIZE = 10

def debug(*msg):
    if os.environ.get("DEBUG"):
        print(*msg)

now = time.ctime(time.time())
debug("Now:", now)
msgBlock = hashlib.sha256()
msgBlock.update(bytes(now, "utf-8"))
msgHash = msgBlock.hexdigest()
debug("Hash:", msgHash)
result = msgHash[:SIZE]
print(result.upper())
