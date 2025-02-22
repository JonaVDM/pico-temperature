import dht
from machine import Pin
from utime import sleep, time
import config
import network
import socket

sensor = dht.DHT22(Pin(15))
last_update = 0
led = Pin(config.PIN_LED, Pin.OUT)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body>
        <h1>Pico W</h1>
    </body>
</html>
"""


def main():
    connect_to_network()
    s = start_server()

    while True:
        try:
            conn, addr = s.accept()
            led.on()
            print('[http] connection received', addr)
            conn.recv(1024)  # browsers do not like it when you don't do a read.

            temp, hum = measure()

            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
            conn.send(content(temp, hum))
            conn.close()
            led.off()
        except Exception as e:
            print(f'[main] error caught: {e}')


def content(temp: int, hum: int):
    return f"""# TYPE pico_temperature gauge
# HELP pico_temperature The temperature in C
pico_temperature {temp}
# TYPE pico_humidity gauge
# HELP pico_humidity The humidity
pico_humidity {hum}
"""


def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(3)
    print('[http] listening on', addr)
    return s


def connect_to_network():
    led.on()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.SSID, config.PASSWORD)
    wlan.ifconfig((config.IP, config.MASK, config.GATEWAY, config.DNS))
    while not wlan.isconnected():
        print(f'[network] waiting for network connection, status: {wlan.status()}')
        sleep(1)
    print(f'[network] connected to the network: {wlan.ifconfig()}')
    led.off()


def measure():
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print(f'[measure] temp = {temp}; hum = {hum}')
    return temp, hum


main()
