from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
from digi.xbee.io import IOLine,IOValue
from digi.xbee.exception import OperationNotSupportedException
from digi.xbee.util import utils
from digi.xbee.models.address import XBee64BitAddress, XBee16BitAddress, XBeeIMEIAddress
from digi.xbee.packets.common import ATCommPacket, TransmitPacket, RemoteATCommandPacket
from digi.xbee.models.mode import OperatingMode

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QLabel, QMainWindow, QMessageBox, QAction, QLineEdit, QPushButton, QFileDialog, QPlainTextEdit, QComboBox
import time
import serial
import os
import sys
import threading

from DHT11 import DHT11

class XBee(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        self.ports = self.get_ports()
        self.initUI()
        self.device = None
        self.dht = None
        
    def initUI(self):               
        
        #label
        self.label_port = QLabel("Port: ", self)
        self.label_port.move(40,40)
        
        self.label_message = QLabel("Message ", self)
        self.label_message.move(40,90)
        
        self.label_port = QLabel("MAC ", self)
        self.label_port.move(40,140)
        
        #combobox
        self.combobox_port = QComboBox(self)
        self.combobox_port.addItems(self.ports)
        self.combobox_port.move(90,40)
        
        #textbox
        self.textbox_message = QLineEdit(self)
        self.textbox_message.move(90, 95)
        self.textbox_message.resize(280,20)
        
        self.textbox_send_address = QLineEdit(self)
        self.textbox_send_address.move(90, 145)
        self.textbox_send_address.resize(280,20)
        
        #text field
        self.textfield_data_received =  QPlainTextEdit(self)
        self.textfield_data_received.move(40,200)
        self.textfield_data_received.resize(400,250)
        self.textfield_data_received.setReadOnly(True)
        
        #button
        self.button_connect = QPushButton("Connect",self)
        self.button_connect.setGeometry(400,40,50,25)
        self.button_connect.clicked.connect(self.open_close_port)
        
        self.button_send = QPushButton("Send",self)
        self.button_send.setGeometry(400,90,50,25)
        self.button_send.clicked.connect(self.send_broadcast)
        
        self.button_toggle = QPushButton("toggle",self)
        self.button_toggle.setGeometry(500,200,50,25)
        self.button_toggle.clicked.connect(self.toggle)
        
        self.button_read_temperature = QPushButton("read t",self)
        self.button_read_temperature.setGeometry(500,300,50,25)
        self.button_read_temperature.clicked.connect(self.read_temp)
        
        self.label_status = QLabel("Status", self)
        self.label_status.move(40,450)
        
        self.setGeometry(300, 200, 700, 500)
        self.setWindowTitle('XBee Test')
        self.show()
        
    def get_ports(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
                
        return result

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure wish to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            try:
                self.close_port()
                event.accept()
            except:
                event.accept()
            
        else:
            event.ignore()   
        
    def open_close_port(self):
        self.com = self.combobox_port.currentText()
                
        if(self.button_connect.text() == "Connect"):
            try:
                self.device = XBeeDevice(self.com,9600)
                self.dht11 = DHT11(self.device,IOLine.DIO3_AD3)
                
                self.device.open()
                self.label_status.setText("connect successfully!")
                self.button_connect.setText("Close")
                
                #set callback
                self.xbee_data_received_callback(self.device)
            except:
                self.label_status.setText("connect fail!")
        elif(self.button_connect.text() == "Close"):
            try: 
                self.close_port()
                self.button_connect.setText("Connect")
                self.label_status.setText("Port closed!")
            except:
                self.label_status.setText("closed fail!")
        
    def send_broadcast(self):
        self.device.send_data_broadcast(self.textbox_message.text())
    
    def my_data_received_callback(self,xbee_message):
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode("utf8")
        
        print("Received data from %s: %s" % (address, data))
        
        #remote_dev = RemoteXBeeDevice(self.device, address)
        #self.device.send_data(remote_dev, "Hello XBee!")
        
        
        threading.Thread(target=self.append, args=[address,data]).start()

        
        ATcommand1 = RemoteATCommandPacket(1,address,XBee16BitAddress.from_hex_string("FFFE"),2,"P2",bytearray([0x05]))
        #raw1 = bytearray([0x7E,0x00,0x10,0x17,0x01,0x00,0x13,0xA2,0x00,0x41,0x47,0x9E,0xC1,0xFF,0xFE,0x02,0x50,0x32,0x05,0xC5])
        #ATpacket1 = RemoteATCommandPacket.create_packet(raw1, OperatingMode.API_MODE)
        #self.device.send_packet(ATcommand1)
        
        #raw2 = bytearray([0x7E,0x00,0x10,0x17,0x01,0x00,0x13,0xA2,0x00,0x41,0x47,0x9E,0xC1,0xFF,0xFE,0x02,0x50,0x32,0x04,0xC6])
        #ATpacket2 = RemoteATCommandPacket.create_packet(raw2, OperatingMode.API_MODE)
        ATcommand2 = RemoteATCommandPacket(1,address,XBee16BitAddress.from_hex_string("FFFE"),2,"P2",bytearray([0x04]))
        #self.device.send_packet(ATcommand2)
        
        ATcommand3 = RemoteATCommandPacket(1,address,XBee16BitAddress.from_hex_string("FFFE"),2,"D4",bytearray([0x05]))
        ATcommand4 = RemoteATCommandPacket(1,address,XBee16BitAddress.from_hex_string("FFFE"),2,"D4",bytearray([0x04]))
        
        for i in range(10):
            self.device.send_packet(ATcommand1)
            self.device.send_packet(ATcommand4)
            time.sleep(1)
            self.device.send_packet(ATcommand2)
            self.device.send_packet(ATcommand3)
            time.sleep(1)
        
        #self.__send_and_sleep(remote_dev,1,0.5)
        #self.__send_and_sleep(remote_dev,0,0.5)
        
    def append(self,address,data):
        self.textfield_data_received.appendPlainText(str(address)+':'+str(data))
    
    def xbee_data_received_callback(self,device):
        device.add_data_received_callback(self.my_data_received_callback)
        
    # def toggle1(self):
        # threading.Thread(target=self.toggle).start()
    def read_temp(self):
        
        def run():
            self.read_input()
        
        threading.Thread(target=run).start()
    
    
    def toggle(self):
        # try:
            # value = self.device.get_adc_value(IOLine.DIO1_AD1)
            # self.label_status.setText(str(value))
        # except OperationNotSupportedException:
            # self.label_status.setText("Answer does not contain analog values for the given IO line")
        def run():   
        #self.device.set_parameter("P2",utils.hex_string_to_bytes("05"))
            for i in range(10):
                t0 = time.time()
                self.__send_and_sleep(self.device,1,0.5)
                self.__send_and_sleep(self.device,0,0.5)
                print(str(time.time() - t0))
                
        threading.Thread(target=run).start()    
    
    def __send_and_sleep(self,dev, output, sleep):
        if(output==1):
            dev.set_parameter("P2",utils.hex_string_to_bytes("05"))
            print("set High")
            print(dev.get_dio_value(IOLine.DIO12))
            time.sleep(sleep)
        elif(output==0):
            dev.set_parameter("P2",utils.hex_string_to_bytes("04"))
            print("set Low")
            print(dev.get_dio_value(IOLine.DIO12))
            time.sleep(sleep)
    
    
    def close_port(self):
        self.device.close()

    
    def read_input(self):
        result = self.dht11.read()
        print(result)
        if result.is_valid():
            print("Last valid input: " + str(datetime.datetime.now()))
            print("Temperature: %d C" % result.temperature)
            print("Humidity: %d %%" % result.humidity)
            

    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = XBee()
    sys.exit(app.exec_())    
    
    
    
    
    