import dht
from machine import Pin
from utime import sleep, time
import config
import ujson
import network
import urequests
import gc

sensor = dht.DHT22(Pin(15))
last_update = 0
led = Pin(config.PIN_LED, Pin.OUT)


def main():
    connect_to_network()

    last_update = 0
    while True:
        if last_update + config.TIMEOUT > time():
            continue
        last_update = time()

        try:
            temp, hum = measure()
            upload(temp, hum)
        except Exception as e:
            print(f'[main] error caught: {e}')
        sleep(1)
        gc.collect()


def connect_to_network():
    led.on()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.SSID, config.PASSWORD)
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


def upload(temperature, humidity):
    led.on()
    data = ujson.dumps({
        'temperature': temperature,
        'humidity': humidity,
    })
    try:
        res = urequests.post(config.URL, headers={'Content-Type': 'application/json'}, data=data)
        print(f'[sender] request send; status: {res.status_code}')
        led.off()
    except Exception as e:
        print(f'[sender] error {e}')


main()
