import threading
import serial
import time
import matplotlib.pyplot as plt 
import numpy as np
global connected
connected = False
import RPi.GPIO as GPIO
import time
import pickle
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT) # Turn on lights
GPIO.setup(24, GPIO.OUT) # Determine color

# What is the file save name

expName = 'baseline Necter6'



#change name of the port here
#port = 'COM4'
port = '/dev/cu.usbmodem1411101'
port = '/dev/ttyACM0'
baud = 230400
global input_buffer
global sample_buffer
global cBufTail
cBufTail = 0
input_buffer = []
sample_rate = 10000
display_size = 10000 #3 seconds
sample_buffer = np.linspace(0,0,display_size)
serial_port = serial.Serial(port, baud, timeout=0)


baseline = 5 # seconds
pulses = 5
interval = 1 
color = 'red' # or 'blue'







if color == 'red':
    GPIO.output(24, GPIO.HIGH)
else:
    GPIO.output(24, GPIO.LOW)


def checkIfNextByteExist():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        
        if tempTail==len(input_buffer): 
            return False
        return True
    

def checkIfHaveWholeFrame():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        while tempTail!=len(input_buffer): 
            nextByte  = input_buffer[tempTail] & 0xFF
            if nextByte > 127:
                return True
            tempTail = tempTail +1
        return False;
    
def areWeAtTheEndOfFrame():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        nextByte  = input_buffer[tempTail] & 0xFF
        if nextByte > 127:
            return True
        return False

def numberOfChannels():
    return 1

def handle_data(data):
    global input_buffer
    global cBufTail
    global sample_buffer    
    if len(data)>0:

        cBufTail = 0
        haveData = True
        weAlreadyProcessedBeginingOfTheFrame = False
        numberOfParsedChannels = 0
        
        while haveData:
            MSB  = input_buffer[cBufTail] & 0xFF
            
            if(MSB > 127):
                weAlreadyProcessedBeginingOfTheFrame = False
                numberOfParsedChannels = 0
                
                if checkIfHaveWholeFrame():
                    
                    while True:
                        
                        MSB  = input_buffer[cBufTail] & 0xFF
                        if(weAlreadyProcessedBeginingOfTheFrame and (MSB>127)):
                            #we have begining of the frame inside frame
                            #something is wrong
                            break #continue as if we have new frame
            
                        MSB  = input_buffer[cBufTail] & 0x7F
                        weAlreadyProcessedBeginingOfTheFrame = True
                        cBufTail = cBufTail +1
                        LSB  = input_buffer[cBufTail] & 0xFF

                        if LSB>127:
                            break #continue as if we have new frame

                        LSB  = input_buffer[cBufTail] & 0x7F
                        MSB = MSB<<7
                        writeInteger = LSB | MSB
                        numberOfParsedChannels = numberOfParsedChannels+1
                        if numberOfParsedChannels>numberOfChannels():
            
                            #we have more data in frame than we need
                            #something is wrong with this frame
                            break #continue as if we have new frame
            

                        sample_buffer = np.append(sample_buffer,writeInteger-512)
                        

                        if areWeAtTheEndOfFrame():
                            break
                        else:
                            cBufTail = cBufTail +1
                else:
                    haveData = False
                    break
            if(not haveData):
                break
            cBufTail = cBufTail +1
            if cBufTail==len(input_buffer):
                haveData = False
                break


def read_from_port(ser):
    global connected
    global input_buffer
    while not connected:
        #serin = ser.read()
        connected = True

        while True:
           
           reading = ser.read(1024)
           if(len(reading)>0):
                reading = list(reading)
#here we overwrite if we left some parts of the frame from previous processing 
#should be changed             
                input_buffer = reading.copy()
                print("len(reading)",len(reading))
                handle_data(reading)
           
           time.sleep(0.001)

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()
xi = np.linspace(-display_size/sample_rate, 0, num=display_size)

saveBin = []

t1 = time.time()
t2 = time.time()
expTime = baseline

while t2-t1 < expTime:
    plt.ion()
    plt.show(block=False)
    if(len(sample_buffer)>0):
        #i = len(sample_buffer)
        print(len(sample_buffer))
        yi = sample_buffer.copy()
        saveBin.append(yi)
        yi = yi[-display_size:]
        sample_buffer = sample_buffer[-display_size:]
        plt.clf()      

        plt.ylim(2000, 15000)
        plt.plot(xi, yi, linewidth=1, color='royalblue')
        plt.pause(0.001)
        time.sleep(0.08)
    t2 = time.time()
    
ii = open('/home/pi/Desktop/beeNeurons/%s'%expName,'wb')
pickle.dump(saveBin,ii)
ii.close()
plt.plot(saveBin[-1])
plt.savefig('/home/pi/Desktop/beeNeurons/%s.jpg'%expName)


thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()
xi = np.linspace(-display_size/sample_rate, 0, num=display_size)

saveBin = []

t1 = time.time()
t2 = time.time()


plt.ion()
plt.show(block=False)

stmm = False
for ppulse in range(0,pulses*2):    
    
    temp  = []
    t1 = time.time()
    t2 = time.time()
    
    stmm = not stmm
    while t2 - t1 < interval:
        if stmm:
            GPIO.output(23, GPIO.HIGH)

        if(len(sample_buffer)>0):
            #i = len(sample_buffer)
            print(len(sample_buffer))
            yi = sample_buffer.copy()
            temp.append(yi)
            yi = yi[-display_size:]
            sample_buffer = sample_buffer[-display_size:]
            plt.clf()      

            plt.ylim(2000, 15000)
            plt.plot(xi, yi, linewidth=1, color='royalblue')
            plt.pause(0.001)
            time.sleep(0.08)
        if stmm:
            GPIO.output(23,GPIO.LOW)
            
        t2 = time.time()
    saveBin.append(temp)
    
    
    
ii = open('/home/pi/Desktop/beeNeurons/%s_pulse'%expName,'wb')
pickle.dump(saveBin,ii)
ii.close()
plt.plot(saveBin[-1][-1])
plt.savefig('/home/pi/Desktop/beeNeurons/%s_pulse.jpg'%expName)
