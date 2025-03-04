# Label your experiment
group_name = 'group_matt'
sampleID = 'flyB'
experimental_condition = 'linalool'


# Load the libraries
import RPi.GPIO as GPIO
import time
import subprocess
import os
import glob
import shutil

# Setting up the GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

# Start the video capture
#test = "/home/pi/Desktop/testTime.avi"
#subprocess.run(["libcamera-vid","-t","145000","--shutter","20000","--width","4056","--height","3040","-o",test])
print('bb')
subprocess.Popen(["sudo","sh","./vidCall.sh"],close_fds=True)
#os.system('sudo sh ./vidCall.sh')
print('pp')
# Pause for 30 seconds
time.sleep(30)


## Lightly pulse the odor for 15 seconds

# repeat these steps 5 times
for inter1 in range(0,5):
    
    #turn on the air pump
    GPIO.output(23,GPIO.HIGH)
    
    # pause for a second
    time.sleep(1)
    
    # turn off the air pump
    GPIO.output(23,GPIO.LOW)
    
    # pause for 2 seconds
    time.sleep(2)
    

# Pause for 15 seconds
time.sleep(15)

# Present the odor for 15 seconds
GPIO.output(23,GPIO.HIGH)
time.sleep(15)

# Turn off the odor
GPIO.output(23,GPIO.LOW)


# Pause for 30 seconds
time.sleep(30)

# Pause for an extra 2 seconds
time.sleep(2)

aFiles = glob.glob('/home/pi/Desktop/temp/*')
aFiles.sort()
tFile = aFiles[-1]
ttName = tFile.split('/')[-1]

tempName = '%s_%s_%s_%s'%(group_name,sampleID,experimental_condition,ttName)
shutil.move(tFile,'/home/pi/Desktop/odorExps/'+tempName)
for ele in aFiles:os.remove(ele)
