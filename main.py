import sys
import time
from queue import Queue

from diablorun_igt.live_split_client import LiveSplitClient
from diablorun_igt.reader import Reader

queue = Queue()

ls_client = LiveSplitClient(queue)
ls_client.start()

if len(sys.argv) > 1:
    reader = Reader(sys.argv[1])
else:
    reader = Reader()

while True:
    try:
        try:
            changes = reader.get_changes()

            for change in changes:
                print(change)
                queue.put_nowait(change)
            
            time.sleep(0.01)
        except Exception:
            print("Unable to read screen")
            time.sleep(1)
    except KeyboardInterrupt:
        queue.put_nowait({ "event": "stop" })
        break

ls_client.join()
