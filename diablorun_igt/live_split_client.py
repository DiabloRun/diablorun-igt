from queue import Empty, Queue
import socket
import threading
import time

class LiveSplitClient(threading.Thread):
    connected = False
    address_str = ""

    def __init__(self, queue: Queue, address=("localhost", 16834)):
        super(LiveSplitClient, self).__init__()

        self.queue = queue
        self.address = address
        self.address_str = address[0] + ":" + str(address[1])
    
    def connect(self):
        try:
            self.s.connect(self.address)
            print("Connected to LiveSplit server at " + self.address_str)
            self.connected = True
        except ConnectionRefusedError:
            print("Could not connect to LiveSplit server at " + self.address_str + ", trying again in 3 seconds")
            self.connected = False
            self.connection_failed_at = time.time()
    
    def run(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

        while True:
            try:
                message = self.queue.get(True, 0.01)

                if message["event"] == "stop":
                    break
                elif self.connected:
                    try:
                        self._send(message)
                    except ConnectionAbortedError:
                        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.connect()
            except Empty:
                pass

            if not self.connected and time.time() - self.connection_failed_at > 3:
                self.connect()
    
    def _send(self, message):
        if message["event"] == "is_loading" and message["value"]:
            self.s.send(b"pausegametime\r\n")
        elif message["event"] == "is_loading" and not message["value"]:
            self.s.send(b"unpausegametime\r\n")
