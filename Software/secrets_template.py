#Secrets template
#  Fill out the information for your wifi and MQTT broker.
#  You can change 'device_name' and 'device_ID' to change how the device appears in your MQTT broker
#    -device_name: Sets the name of the sensor in Home Assistant.
#     'Temperature', 'Pressure' and 'Humidity' are appended to this name to set the sensor names.
#    -device_ID: Sets the MQTT state and config topic names. Also used as the hostname of the device.
#     Topic names are made in the form: 'homeassistant/sensor/device_ID/state'
#     Use only letters and numbers for this one (no spaces or special characters)
#  timezone is the offset from UTC in hours. Can be positive or negative. Setting the timezone is optional.
#
#  When you are done, save this file to your device with the name 'secrets.py'


secrets = {
    'ssid' : '<your SSID here>',
    'password' : '<your wifi password here>',
    'device_name' : 'Weather Station',
    'device_ID' : 'WeatherStation',
    'mqtt_broker_ip' : '<IP address of your MQTT broker here>',
    'mqtt_broker_port' : '1883',
    'mqtt_broker_user' : '<Username of your MQTT broker here>',
    'mqtt_broker_pass' : '<password for your MQTT broker here>',
    'timezone' : "<Your timezone offset here>"
    }
