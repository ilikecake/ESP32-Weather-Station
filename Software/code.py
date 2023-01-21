import board
import time
import json
import ipaddress
import ssl

import rtc
import adafruit_ntp

import wifi
import socketpool
import adafruit_requests
import neopixel
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))

def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))


def message(client, topic, message):
    # Method called when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

def ConnectToWifi():
    global secrets
    Retries = 0

    while True:
        if Retries > 1000:
            microcontroller.reset()
        else:
            Retries = Retries + 1
        try:
            wifi.radio.connect(secrets["ssid"], secrets["password"])
        except Exception as e:  # pylint: disable=broad-except
            print("Failed to connect to WiFi. Error:", e)
        else:
            if wifi.radio.ipv4_address is not None:
                return
        time.sleep(30)

#Define MQTT variables
MQTT_State_Topic = "homeassistant/sensor/" + secrets["device_ID"] + "/state"
MQTT_Config_Temp = "homeassistant/sensor/"+secrets["device_ID"]+"_temp/config"
MQTT_Config_Humidity = "homeassistant/sensor/"+secrets["device_ID"]+"_humidity/config"
MQTT_Config_Pressure = "homeassistant/sensor/"+secrets["device_ID"]+"_pressure/config"

MQTT_Config_Temp_Payload = json.dumps({"device_class":           "temperature", \
                                       "name":                   secrets["device_name"] + " Temperature", \
                                       "state_topic":            MQTT_State_Topic, \
                                       "unit_of_measurement":    "°F", \
                                       "value_template":         "{{value_json.temperature}}" })

MQTT_Config_Humidity_Payload = json.dumps({"device_class":           "humidity", \
                                           "name":                   secrets["device_name"] + " Humidity", \
                                           "state_topic":            MQTT_State_Topic, \
                                           "unit_of_measurement":    "%", \
                                           "value_template":         "{{value_json.humidity}}" })

MQTT_Config_Pressure_Payload = json.dumps({"device_class":           "pressure", \
                                           "name":                   secrets["device_name"] + " Pressure", \
                                           "state_topic":            MQTT_State_Topic, \
                                           "unit_of_measurement":    "hPa", \
                                           "value_template":         "{{value_json.pressure}}" })





pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
i2c = board.STEMMA_I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

pixel.fill((50, 0, 0))



print("Weather Station ESP32-S2")

ConnectToWifi()

print("Wifi Connected to %s!"%secrets["ssid"])
print("Asigned IP address: ", wifi.radio.ipv4_address)

pixel.fill((0, 50, 0))  #Green
time.sleep(.5)
pixel.fill((0, 0, 0))   #Off

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["mqtt_broker_ip"],
    port=int(secrets["mqtt_broker_port"]),
    username=secrets["mqtt_broker_user"],
    password=secrets["mqtt_broker_pass"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message



print("Connecting to MQTT broker at %s..." % mqtt_client.broker)
#TODO: Should this be a subfunction?
Retries = 0
while True:
    if Retries > 1000:
        microcontroller.reset()
    else:
        Retries = Retries + 1

    try:
        mqtt_client.connect()       #TODO: This command blocks until a connection is established. Do I need to have the rest of this code here?
        mqtt_client.publish(MQTT_Config_Temp, MQTT_Config_Temp_Payload)
        mqtt_client.publish(MQTT_Config_Humidity, MQTT_Config_Humidity_Payload)
        mqtt_client.publish(MQTT_Config_Pressure, MQTT_Config_Pressure_Payload)
    except Exception as e:  # pylint: disable=broad-except
        print("Failed to connect to MQTT. Error:", e, "\nRetry in 30 seconds.")
        time.sleep(30)
    else:
        break
print("Connected to broker.")

print("Setting time from NTP")
Retries = 0
while True:
    if Retries > 1000:
        microcontroller.reset()
    else:
        Retries = Retries + 1

    try:
        TZ_OFFSET = -6  # time zone offset in hours from UTC
        ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)
        rtc.RTC().datetime = ntp.datetime
    except Exception as e:  # pylint: disable=broad-except
        print("Failed to get time from NTP. Error:", e, "\nRetry in 30 seconds.")
        time.sleep(30)
    else:
        break

while True:
    temp_C = bme280.temperature
    temp_F = (temp_C * 9/5) + 32
    humid = bme280.humidity
    press = bme280.pressure
    print("\nTemperature: %0.1f F" % temp_F)
    print("Humidity: %0.1f %%" % humid)
    print("Pressure: %0.1f hPa" % press)


    try:
        mqtt_client.loop()
        mqtt_client.publish(MQTT_State_Topic, json.dumps({"temperature": temp_F, "humidity": humid, "pressure": press}))
    except (ValueError, RuntimeError, MQTT.MMQTTException) as e:
        pixel.fill((50, 50, 0)) #yellow
        print("MQTT Error, retrying\n", e)
        ConnectToWifi()
        mqtt_client.reconnect()
        continue

#This happens if I unplug the broker, it is not caught by the above.
#Traceback (most recent call last):
#  File "code.py", line 194, in <module>
#  File "adafruit_minimqtt/adafruit_minimqtt.py", line 827, in loop
#  File "adafruit_minimqtt/adafruit_minimqtt.py", line 567, in ping
#MMQTTException: PINGRESP not returned from broker.

    pixel.fill((0, 50, 0))
    time.sleep(.25)
    pixel.fill((0, 0, 0))
    time.sleep(9.75)
