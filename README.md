# BirdPics

### HARDWARE USED ###  
The hardware is a Rasberry Pi 3b+ ($35, https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus), Pi Camera V2 ($30, https://www.raspberrypi.org/products/camera-module-v2/),
32GB Samsung SD card ($7.50), Adafruit PIR sensor ($10, https://www.adafruit.com/product/189), and Adafruit Pi battery pack ($40, https://www.adafruit.com/product/1566)

Min cost = $72.5 (no battery/sensor, shipping/handling not included. Use the "timer" branch if there's no sensor).

No-battery cost = $82.5 (use either branch, works anywhere with power)

Cost with battery/sensor = $122.5 (works anywhere, needs charging about once a day - I recommend charging overnight)

### SOFTWARE USED ###
Raspberry Pi OS, this repo

### SETUP ###
Install the OS to the SD card (guide at https://www.raspberrypi.org/downloads/). Once installed, connect the Pi to your Wifi (you can connect it to your monitor over HDMI, then use a USB keyboard/mouse to control it)

Next, add this software to the PI (I suggest making a folder in /home/pi, then cloning the repo into that folder. 
Example: Open a terminal with Ctrl+Alt+T. Enter "mkdir birds" to make a folder, "cd birds" to move into the folder, "sudo apt-get install git" to get git running, then "git clone https://github.com/Dernas/BirdPics.git"
to get this code. If you don't want to do all that, just download BirdSpotter.py, date.txt, and count.text to the Pi.)

There are many ways to run this process at startup. I used systemd (suggested by https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/).
Example: In a terminal, enter "sudo nano /lib/systemd/system/birds.service" to make a service file, then entered:
 [Unit]
 Description=My Sample Service
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/usr/bin/python /home/pi/sample.py

 [Install]
 WantedBy=multi-user.target
 
