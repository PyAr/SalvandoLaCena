import socket
import time

import machine
import network

adc = machine.ADC(0)
led = machine.Pin(2, machine.Pin.OUT)  # "active low"; IOW "inversed"

# set up AP
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='ESP-AP', password="juegopycamp")

# flash the led to indicate it's ready
for i in range(5):
    led.on()  # actually, turn off
    time.sleep(.1)
    led.off()  # actually, turn on
    time.sleep(.4)

# set up socket and wait
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
client, _ = s.accept()

# read the ADC when indicated, flash the led for fancyness
while True:
    client.recv(1)
    led.on()  # actually, turn off
    value = adc.read()
    print("value:", value)
    client.write(str(value).encode("ascii"))
    led.off()  # actually, turn on
