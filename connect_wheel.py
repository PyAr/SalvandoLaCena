import socket
import time

s = socket.socket()
s.connect(('192.168.4.1', 80))
try:

    while True:
        time.sleep(.1)
        s.send(b"\xFF")
        raw = s.recv(10)
        print(int(raw.decode("ascii")))

except KeyboardInterrupt:
    pass

