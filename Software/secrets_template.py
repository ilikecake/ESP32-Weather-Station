#Device specific configuration entries and passwords. For obvious reasons, don't share this 
#file once you have customized it. Fill out the below info and save this file as 'secrets.py'
#in the same folder as the 'code.py' file.

secrets = {
    #Put your wifi SSID here
    'ssid' : '<your SSID here>',
    
    #The password to your wifi goes here
    'password' : '<your wifi password here>',
    
    #Human readable name for this device. This is how it shows up in Homeassistant.
    'device_name' : 'Weather Station',
    
    #Simplified name of the device. Use only alphanumerics, spaces and special characters 
    #are probably bad. This will be the hostname of the device on the network and the prefix
    #for some of the MQTT topics.
    'device_ID' : 'WeatherStation',
    
    #The IP address of your MQTT broker (Home Assistant)
    'mqtt_broker_ip' : '<IP address of your MQTT broker here>',
    
    #The port that your MQTT broker listens on. Default is 1883
    'mqtt_broker_port' : '1883',
    
    #The user to use to connect to the MQTT broker.
    'mqtt_broker_user' : '<Username of your MQTT broker here>',
    
    #The password to use to connect to the MQTT broker.
    'mqtt_broker_pass' : '<password for your MQTT broker here>',
    
    #The server or pool to use for NTP time. This can be set to the IP address of a local NTP server
    #or an internet based NTP pool. You can also set it to blank ('') to skip setting time.
    'NTP_ip' : '0.pool.ntp.org',
    
    #Your timezone in hours (+ or -) from GMT
    'timezone' : "<Your timezone offset here>",
    
    #A unique ID for the device. What you put here is not critical, but it *must* be
    #unique on your network or bad things will happen to your MQTT server. This can be
    #the name of the device, or you can generate a 'real' random UUID from various sources.
    #This UUID will be part of the prefix for the MQTT topics, and will be provided to
    #Homeassistant so that you can properly configure the device.
    'UUID' : '',
    }
