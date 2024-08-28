import serial
import time
import subprocess
import glob
import os


ser = None
ser1 = None #serial.Serial('/dev/ttyUSB5', 9600, timeout=1)
phone_number = '05052590400'
GPSLocation = '39.555489,32.556988'
rec_buff = ''
text_wav = "main.wav"
textout_wav = "mainout.wav"
Latitude = GPSLocation[:9]
Longitude = GPSLocation[10:]
message = "This is an emergency message. The Baby stuck in the car GPS Cordinate is: " + "\r Latitude: "+ Latitude + "\r Longitude: " + Longitude
phoen_call = "There is. an emergency. call. The Baby stuck in the car. GPS. Cordinate. is:"


def initialize_serial():
    global ser
    usb_ports = glob.glob('/dev/ttyUSB*')
    
    while True:  # Loop indefinitely until a response is received
        for i in usb_ports:
            try:
                test_ser = serial.Serial(i, baudrate=115200, timeout=1)
                test_ser.write(b'AT\r')
                
                response = test_ser.readall().decode('utf-8').strip()
                if 'OK' in response:
                    print(f'Response from {i}: {response}')
                    ser = test_ser
                    return  # Exit the function once a successful response is received
                else:
                    print(f'No response from {i}')
                test_ser.close()
            except serial.SerialException as e:
                print(f'Failed to open {i}: {e}')
            except BrokenPipeError as e:
                print(f'Broken pipe on {i}: {e}')
        
        print("No valid response from any USB port. Retrying...")
        time.sleep(5)  # Wait before retrying
        
def initialize_serial_esp32():
    global ser1
    usb_ports = glob.glob('/dev/ttyUSB*')
    
    while True:  # Loop indefinitely until a response is received
        for i in usb_ports:
            try:
                test_ser = serial.Serial(i, baudrate=115200, timeout=1)
                test_ser.write(b'R\r')
                time.sleep(2)
                response = test_ser.readall().decode('utf-8').strip()
                if 'E' in response:
                    print(f'Response from {i}: {response}')
                    ser1 = test_ser
                    return  # Exit the function once a successful response is received
                else:
                    print(f'No response from {i}')
                test_ser.close()
            except serial.SerialException as e:
                print(f'Failed to open {i}: {e}')
            except BrokenPipeError as e:
                print(f'Broken pipe on {i}: {e}')
        
        print("No valid response from any USB port. Retrying...")
        time.sleep(5)  # Wait before retrying

        
         
def txttovoice(text, voice_folder, speed):

    subprocess.call(['flite', '-voice', 'slt', '-t', text, '-o', text_wav])
    subprocess.call(['sox', text_wav, textout_wav, 'tempo', str(speed)])
    subprocess.call(['aplay', text_wav])
    
def txttovoicenumber(text, voice_folder, speed):
    output_wav = f'{voice_folder}/GPS.wav'
    wav_files = []

    # Noktayı "nokta" olarak seslendirmek için karakterleri kontrol et
    for i, char in enumerate(text):
        if char == '.':
            
            char = 'point'
        elif char == ',':
            char = ''
        
        input_wav = f'{voice_folder}/char_{i}.wav'
        subprocess.call(['flite', '-voice', 'slt', '-t', char, '-o', input_wav])
        wav_files.append(input_wav)

    # Sox ile birleştir ve yavaşlat
    subprocess.call(['sox'] + wav_files + [output_wav, 'tempo', str(speed)])
    
    # Geçici dosyaları temizle
    for wav_file in wav_files:
        os.remove(wav_file)
     
    subprocess.call(['aplay', output_wav])   

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
            rec_buff = ser.read_all().decode('utf-8').strip()
            print(f"rec_buff = {rec_buff}")
            if 'VOICE CALL: BEGIN' in rec_buff:
                call_answered = True
                print("Call answered")
                txttovoice("This is. an emergency. call. Baby. stuck. in. the car. GPS. Cordinate. is:","/home/pi/Baby-1/voicecodetext.wav",0.7)
                txttovoice("Latitude.","/home/pi/Baby-1/voicecodetext.wav",0.7)
                txttovoicenumber(Latitude, "/home/pi/Baby-1", 0.8)
                txttovoice("Longitude.","/home/pi/Baby-1/voicecodetext.wav",0.7)
                txttovoicenumber(Longitude, "/home/pi/Baby-1", 0.7)
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

def send_sms():
    print('Begin')
    time.sleep(0.5)
    ser.write(b'ATZ\r')
    time.sleep(0.5)
    ser.write(b'AT+CMGF=1\r')
    time.sleep(0.5)
    ser.write(b'AT+CMGS="' + phone_number.encode() + b'"\r')
    time.sleep(0.5)
    ser.write(message.encode() + b"\r")
    print('sending')
    time.sleep(0.5)
    print('send success')
    ser.write(bytes([26]))
    time.sleep(0.5)

try:
    # initialize_serial()  
    time.sleep(5)
    initialize_serial_esp32()
    # print(ser)
    # print(ser1)
    while True:
        if ser1.in_waiting > 0:
            line = ser1.readline().decode('utf-8', errors='ignore').rstrip()
            print(f"Received: {line}")
            
            if "GPS " in line:
                GPSLocation = line.split("GPS ")[1].strip()
                print(GPSLocation)
                time.sleep(1)            
            if "SMS " in line:
                phone_number = line.split("SMS ")[1].strip()
                print(phone_number)
                time.sleep(1)
                print('sending sms')
                # send_sms()
            if "Call " in line:
                phone_number = line.split("Call ")[1].strip()
                print(phone_number)
                time.sleep(1)
                print('making phone call')
                # phone()
           
        time.sleep(1)

except KeyboardInterrupt:
    print("Program END")

finally:
    # if ser:
    #     ser.close()
    if ser1:
        ser1.close()