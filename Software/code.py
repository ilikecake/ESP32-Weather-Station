import board
import time
import json
import ipaddress
import ssl
import microcontroller

import rtc
import adafruit_ntp

import wifi
import socketpool
import adafruit_requests
import neopixel
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_minimqtt.adafruit_minimqtt as MQTT

#Controls the timeout when connecting to wifi, MQTT, and NTP
# The code will try to connect 'TIMEOUT_COUNTS' number of times, and wait 'RETRY_DELAY' seconds between each try.
# After it reaches the timeout, it will hard reset the device.
# Default values of 200 and 30sec means that the device will try to connect for ~1 hour 40 min before rebooting.
TIMEOUT_COUNTS = 200
RETRY_DELAY = 30        #sec
NTP_Time_Set = False

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
i2c = board.STEMMA_I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
#TODO: Do I need any of these?
def connect(mqtt_client, userdata, flags, rc):
    pass
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    #print("Connected to MQTT Broker!")
    #print("Flags: {0}\n RC: {1}".format(flags, rc))

def disconnect(mqtt_client, userdata, rc):
    pass
    # This method is called when the mqtt_client disconnects
    # from the broker.
    #print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    pass
    # This method is called when the mqtt_client subscribes to a new feed.
    #print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    pass
    # This method is called when the mqtt_client unsubscribes from a feed.
    #print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    pass
    # This method is called when the mqtt_client publishes data to a feed.
    #print("Published to {0} with PID {1}".format(topic, pid))


def message(client, topic, message):
    pass
    # Method called when a client's subscribed feed has a new value.
    #print("New message on topic {0}: {1}".format(topic, message))

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

def ConnectToNetwork():
    global pixel
    global mqtt_client
    Retries = 0

    #Connect to wifi
    print("Connecting to SSID: {0:s}...".format(secrets["ssid"]), end =".")
    if wifi.radio.ipv4_address is None:
        ConnectToWifi()
        print("ok")
    else:
        print("already connected")
    print("  IP: ", wifi.radio.ipv4_address)

    #Connect to MQTT broker
    Retries = 0
    print("Connecting to MQTT broker at %s..." % mqtt_client.broker, end =".")
    pixel.fill((0, 0, 50))  #Blue

    while True:
        if Retries > TIMEOUT_COUNTS:
            microcontroller.reset()
        else:
            Retries = Retries + 1

        if wifi.radio.ipv4_address is not None:     #TODO: if the wifi connection is lost, I think the IP address becomes none. I should test this...
            try:
                mqtt_client.connect()       #This command has a built in retry/timeout thing, so it takes about 3 min to fail.
                mqtt_client.publish(MQTT_Config_Temp, MQTT_Config_Temp_Payload)
                mqtt_client.publish(MQTT_Config_Humidity, MQTT_Config_Humidity_Payload)
                mqtt_client.publish(MQTT_Config_Pressure, MQTT_Config_Pressure_Payload)
            except Exception as e:  # pylint: disable=broad-except
                print("Failed ({0:d}/{1:d}). Error:".format(Retries, TIMEOUT_COUNTS), e)
                time.sleep(RETRY_DELAY)     #Note: there is a delay/retry built into the connect function also, so this will take longer than you think.
            else:
                #We are connected to wifi and the MQTT broker.
                pixel.fill((0, 0, 0))  #Off
                break
        else:
            #This could happen if the wifi connection is lost as we are trying to connect to the MQTT broker.
            print("Connecting to SSID: {0:s}...".format(secrets["ssid"]), end =".")
            ConnectToWifi()
            print("ok")
            print("  IP: ", wifi.radio.ipv4_address)
            print("Connecting to MQTT broker at %s..." % mqtt_client.broker, end =".")
            pixel.fill((0, 0, 50))  #Blue
    print("ok")

def ConnectToWifi():
    global pixel
    Retries = 0

    pixel.fill((50, 0, 0))  #Red
    wifi.radio.hostname = secrets["device_ID"]

    while True:
        if Retries > TIMEOUT_COUNTS:
            microcontroller.reset()
        else:
            Retries = Retries + 1
        try:
            wifi.radio.connect(secrets["ssid"], secrets["password"])
        except Exception as e:  # pylint: disable=broad-except
            print("Failed to connect to WiFi ({0:d}/{1:d}). Error: ".format(Retries, TIMEOUT_COUNTS), e)
            time.sleep(RETRY_DELAY)
        else:
            if wifi.radio.ipv4_address is not None:
                pixel.fill((0, 0, 0))  #Off
                return

def ConnectToMQTT():    #TODO: not used, delete
    global mqtt_client
    global pixel
    Retries = 0

    pixel.fill((0, 0, 50))  #Blue

    while True:
        if Retries > TIMEOUT_COUNTS:
            microcontroller.reset()
        else:
            Retries = Retries + 1

        try:
            mqtt_client.connect()       #TODO: This command blocks until a connection is established. Do I need to have the rest of this code here?
            mqtt_client.publish(MQTT_Config_Temp, MQTT_Config_Temp_Payload)
            mqtt_client.publish(MQTT_Config_Humidity, MQTT_Config_Humidity_Payload)
            mqtt_client.publish(MQTT_Config_Pressure, MQTT_Config_Pressure_Payload)
        except Exception as e:  # pylint: disable=broad-except
            print("Failed to connect to MQTT ({0:d}/{1:d}). Error:".format(Retries, TIMEOUT_COUNTS), e)
            time.sleep(RETRY_DELAY)
        else:
            pixel.fill((0, 0, 0))  #Off
            break

#This function has a shorter timeout delay and timeout count than the wifi and MQTT connect functions
# This is because NTP is not required for the device to function, and I don't want the device to stop working if external internet access is lost.
# If this function times out, the device will keep working and periodically check again for NTP access.
# This function will take ~5*5=25 sec to timeout. If you want to have updates faster than that, this will cause problems.
def GetTimeFromNTP():
    global pixel
    NTP_Retries = 5
    NTP_Retry_Delay = 5
    Retries = 0

    pixel.fill((50, 50, 50))  #White
    while True:
        if Retries > NTP_Retries:
            return False
        else:
            Retries = Retries + 1

        try:
            TZ_OFFSET = int(secrets["timezone"]) # time zone offset in hours from UTC
            ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)
            rtc.RTC().datetime = ntp.datetime
        except Exception as e:  # pylint: disable=broad-except
            print("Failed to get time from NTP. Error ({0:d}/{1:d}):".format(Retries, NTP_Retries), e)
            time.sleep(NTP_Retry_Delay)
        else:
            #NTP_Time_Set = True
            pixel.fill((0, 0, 0))  #Off
            return True

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

print("Weather Station ESP32-S2")
print('MAC Address: {0:X}:{1:X}:{2:X}:{3:X}:{4:X}:{5:X}'.format(wifi.radio.mac_address[0],wifi.radio.mac_address[1],wifi.radio.mac_address[2],wifi.radio.mac_address[3],wifi.radio.mac_address[4],wifi.radio.mac_address[5]))

ConnectToNetwork()

#print("Connecting to SSID: {0:s}...".format(secrets["ssid"]), end =".")
#ConnectToWifi()
#print("ok")
#print("  IP: ", wifi.radio.ipv4_address)

#print("Connecting to MQTT broker at %s..." % mqtt_client.broker, end =".")
#ConnectToMQTT()
#print("ok")

print("Setting time from NTP...", end =".")
NTP_Time_Set = GetTimeFromNTP()
if NTP_Time_Set:
    print("ok")
else:
    print("skipped")
print("Startup Complete")

pixel.fill((0, 0, 0))  #Off

NTP_Retry = 0

while True:

    #If we don't have a valid time from NTP, try to get it here
    #Time is not required, so the get time function will return
    if not NTP_Time_Set:
        if NTP_Retry > 100:
            NTP_Time_Set = GetTimeFromNTP()
        if NTP_Time_Set:
            NTP_Retry = 0
        else:
            NTP_Retry = NTP_Retry + 1

    now = time.localtime()
    temp_C = bme280.temperature
    temp_F = (temp_C * 9/5) + 32
    humid = bme280.humidity
    press = bme280.pressure

    print('{0:02d}:{1:02d}:{2:02d}: T:{3:.4f}, P:{4:.4f}, H:{5:.4f}'.format(now.tm_hour, now.tm_min, now.tm_sec, temp_F, press, humid))

    try:
        mqtt_client.loop()
        mqtt_client.publish(MQTT_State_Topic, json.dumps({"temperature": temp_F, "humidity": humid, "pressure": press}))
    except (ValueError, RuntimeError, OSError, MQTT.MMQTTException) as e:
        #If MQTT broker disappears: MMQTTException: PINGRESP not returned from broker.
        #If wifi AP disappears: OSError: [Errno 113] ECONNABORTED
        pixel.fill((50, 50, 0)) #yellow
        NTP_Retry = 0
        print("Error sending data: ", e)
        ConnectToNetwork()
        #ConnectToWifi()
        #ConnectToMQTT()
        NTP_Time_Set = GetTimeFromNTP()
        continue

    pixel.fill((0, 50, 0))
    time.sleep(.25)
    pixel.fill((0, 0, 0))
    time.sleep(9.75)
