#!/usr/bin/python

import serial
import time
import subprocess
import glob
import os

ser = serial.Serial("/dev/ttyUSB2",115200, timeout=5)
time.sleep(2)  # Seri port açıldıktan sonra kısa bir bekleme
#ser.flushInput()
phone_number = '05052590400'
rec_buff = ''

def phone():
    global rec_buff
    try:
        ser.write(b'ATD' + phone_number.encode() + b';' + b'\r')
        time.sleep(2)
        # rec_buff = ''
        for i in range(20):
            time.sleep(0.01)
            rec_buff = ser.readall().decode('utf-8').strip()
            print(f"rec_buff = {rec_buff}")
    except serial.SerialException as e:
        print(f"Seri port hatası: {e}")
    finally:
        ser.close()  # Seri portu kapatıyoruz

            
phone()


