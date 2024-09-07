import serial
import time
import subprocess
import glob
import os


# ser = None
ser = serial.Serial('/dev/ttyUSB3', baudrate=115200, timeout=1)
phone_number = '05052590400'
rec_buff = ''
text_wav = "main.wav"
textout_wav = "mainout.wav"
print('1')
# def initialize_serial():
#     global ser
#     usb_ports = glob.glob('/dev/ttyUSB*')
    
#     while True:  # Loop indefinitely until a response is received
#         for i in usb_ports:
#             try:
#                 test_ser = serial.Serial(i, baudrate=115200, timeout=1)
#                 test_ser.write(b'AT\r')
                
#                 response = test_ser.readall().decode('utf-8').strip()
#                 if 'OK' in response:
#                     print(f'Response from {i}: {response}')
#                     ser = test_ser
#                     return  # Exit the function once a successful response is received
#                 else:
#                     print(f'No response from {i}')
#                 test_ser.close()
#             except serial.SerialException as e:
#                 print(f'Failed to open {i}: {e}')
#             except BrokenPipeError as e:
#                 print(f'Broken pipe on {i}: {e}')
        
#         print("No valid response from any USB port. Retrying...")
#         time.sleep(5)  # Wait before retrying

def txttovoice(text, voice_folder, speed):

    subprocess.call(['flite', '-voice', 'slt', '-t', text, '-o', text_wav])
    subprocess.call(['sox', text_wav, textout_wav, 'tempo', str(speed)])
    subprocess.call(['aplay', text_wav])


def phone():
    attempts = 0
    max_attempts = 3
    call_answered = False
    
    while attempts < max_attempts and not call_answered:
        attempts += 1
        print(f"Attempt {attempts}")
        
        ser.write(b'ATD' + phone_number.encode() + b';' + b'\r')
        time.sleep(2)
        
        for i in range(20):
            time.sleep(0.01)
            rec_buff = ser.readall().decode('utf-8').strip()
            print(f"rec_buff = {rec_buff}")
            if 'VOICE CALL: BEGIN' in rec_buff:
                call_answered = True
                print("Call answered")
                txttovoice("This is. an emergency. call. Baby. stuck. in. the car. GPS. Cordinate. is:","/home/pi/CarsafeClimateAlert/voicecodetext.wav",0.7)
                txttovoice("Latitude.","/home/pi/CarsafeClimateAlert/voicecodetext.wav",0.7)
                time.sleep(5)
                break
            elif 'NO CARRIER' in rec_buff:
                print("Call not answered")
                break
            time.sleep(1)
        if call_answered:
            ser.write(b'AT+CHUP\r\n')  # Disconnect the call 
            break
        if not call_answered:
            ser.write(b'AT+CHUP\r\n')  
            print("Call disconnected")
            time.sleep(5)

    if call_answered:
        print("Call successfully answered after", attempts, "attempt(s)")
    else:
        print("Call not answered after 3 attempts")
print('2')
try:
    print('3')
    # initialize_serial()  
    print('4')
    time.sleep(5)
    print('5')
    phone()
    print('6')

except KeyboardInterrupt:
    print("Program END")

finally:
    if ser:
        ser.close()
