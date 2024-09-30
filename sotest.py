import serial
import time

# Setup serial communication with the SIM7600
ser = serial.Serial('/dev/ttyUSB2', baudrate=115200, timeout=1)

def place_call(number):
    # Dial the number
    ser.write(f'ATD{number};\r'.encode())

def monitor_call():
    while True:
        response = ser.readline().decode('utf-8').strip()
        if response:
            print(f"Modem response: {response}")
            if "CONNECT" in response:
                print("Call answered!")
                break
            elif "NO CARRIER" in response:
                print("Call ended or failed.")
                break
            elif "BUSY" in response:
                print("User busy.")
                break 

# Place a call and monitor its status
place_call("05052590400")
monitor_call()