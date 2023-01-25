# ESP32 Weather Station

This project is a temperature, humidity and barometric pressure sensor housed in a 3D printed case. It is designed to be placed in a protected place outside, and report sensor readings periodically over MQTT. It uses a small ESP32 for wifi communication, and requires a 5Vdc power source. 

<img src="https://github.com/ilikecake/ESP32-Weather-Station/blob/main/Assets/Placement-final.JPG" height="200">  [<img src="https://github.com/ilikecake/ESP32-Weather-Station/blob/main/Assets/Assy-arrange_wires_1.JPG" height="200">](https://github.com/ilikecake/ESP32-Weather-Station/blob/main/Assets/Assy-arrange_wires_1.JPG)

Features
* Temperature/Humidity/Pressure sensor: BME280.
* 3D printed case is designed to allow airflow around the sensor.
* Powered by 5V (standard USB power supplies will work)
* Wifi connectivity, reports sensor readings to an MQTT broker.

Building this project will require:
* 3D printer to print the case components.
* Basic soldering capability for the wiring.
* A reasonably protected location to install the sensor.

For information on how to build this project and usage of the software, refer to the wiki.
