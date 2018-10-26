# Xbee-examples-python
Some examples of playing with Xbee

# Abstract
- Internet-of-thing or IOT is becoming essential in the modern life. It's fun and enthusiastic to programme something that can automatically do something without interferences of human.
- Xbee devices provide a comprehensive way to control devices from family scale to industrial scale. It's an easy-to-use wireless communication module that can be programmed or controlled with external microcontrollers. I myself find it interesting and enthusiastic when playing with this XBee devices. Therefore I want to share my joyness to all of you through this very simple example.
![Alt text](https://github.com/habom2310/Xbee-examples-python/blob/master/zigbee_kit.jpg)

_I'm just an user of Xbee, not a commercial agent_
# Requirements
- Zigbee kit
- Breadboard
- Leds
- DTH11 (temperature sensor)

- XCTU software
- python-xbee [see it here](https://github.com/digidotcom/python-xbee)

# Implementation
- Connect XBee devices to your computer through USB.
- Open XCTU and connect serial with XBee devices and configuration them to be in the same network. See how to use XCTU _*-->[here](https://www.digi.com/resources/documentation/Digidocs/90001942-13/#concepts/c_xbee_zigbee_mesh_kit.htm%3FTocPath%3D_____1)<--*_.
- Run `python connect.py` , select the serial port of another XBee and connect to it.
- Here are things you can do:
  - Send messages broadcast to all other XBees in the same network.
  - Connect a led to DIO12. Press 'toggle' to turn it on/off for 10 times.
  - Connect the DTH11 to the DIO3. Press 'read t' to get the temperature.
  - Connect a led to DIO4. In XCTU, send a message to the XBee connected to the app. The message will be shown in the text area and also trigger a callback that respectively turn on/off leds in DIO12 and DIO4.

# TODO
- This is just a very simple example to understand the XBee. A lot of interesting things can be developed in the future.
- Any new idea is welcome, contact me at khanhhanguyen2310@gmail.com
