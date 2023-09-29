import dht
from machine import Pin
from utime import sleep
import config
import ujson
import network
import urequests
import utime as time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PASSWORD)

sensor = dht.DHT22(Pin(15))
last_update = 0

while True:
    if last_update + config.TIMEOUT > time.time():
        continue
    last_update = time.time()

    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        data = ujson.dumps({'temperature': temp, 'humidity': hum})
        res = urequests.post(config.URL, headers = {'Content-Type': 'application/json'}, data = data)
        print(res)

        print('Temperature: %3.1f C' % temp)
        print('Humidity: %3.1f %%' % hum)
        sleep(1)
    except OSError as e:
        print('Failed to read sensor.', e)
