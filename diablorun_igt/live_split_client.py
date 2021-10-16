import socket
import time


class LiveSplitClient:
    def __init__(self, address=("localhost", 16834)):
        self.address = address
        self.address_str = address[0] + ":" + str(address[1])
        self.connected = False
        self.connection_failed_at = None
        self.running = False

    def connect(self):
        try:
            self.s.connect(self.address)
            print("Connected to LiveSplit server at " + self.address_str)
            self.connected = True
        except ConnectionRefusedError:
            print("Could not connect to LiveSplit server at " +
                  self.address_str + ", trying again in 1 second...")
            self.connected = False
            self.connection_failed_at = time.time()

    def run(self):
        self.running = True
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

        while self.running:
            """
            try:
                message = self.queue.get(True, 0.01)

                if self.connected:
                    try:
                        self._send(message)
                    except ConnectionAbortedError:
                        self.s = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
                        self.connect()
            except Empty:
                pass
            """

            if not self.connected and time.time() - self.connection_failed_at > 1:
                self.connect()

            time.sleep(0.01)

    def _send(self, message):
        if not self.connected:
            return

        try:
            self.s.send(message)
        except ConnectionAbortedError:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False
            self.connection_failed_at = time.time()

    def pause(self):
        self._send(b"pausegametime\r\n")

    def unpause(self):
        self._send(b"unpausegametime\r\n")

    def stop(self):
        self.running = False
