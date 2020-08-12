# BirdPics

### HARDWARE USED ###  
The hardware is a Rasberry Pi 3b+ ($35, https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus), Pi Camera V2 ($30, https://www.raspberrypi.org/products/camera-module-v2/),
32GB Samsung SD card ($7.50), Adafruit PIR sensor ($10, https://www.adafruit.com/product/189), and Adafruit Pi battery pack ($40, https://www.adafruit.com/product/1566)

Min cost = $72.5 (no battery/sensor, shipping/handling not included. Use the "timer" branch if there's no sensor).

No-battery cost = $82.5 (use either branch, works anywhere with power)

Cost with battery/sensor = $122.5 (works anywhere, needs charging about once a day - I recommend charging overnight)

### SOFTWARE USED ###
Raspberry Pi OS & this repo

### SETUP ###

## Hardware ##

1. Camera: Connect the Pi to the camera as described in camera instructions. 

2. Sensor: Solder pin headers to the connectors, then connect the red wire to pin 4, yellow to pin 29, and black to pin 20. (see https://www.raspberrypi.org/documentation/usage/gpio/ for pin numbers)

3. Battery: After charging the battery with any USB-compatible power block, plug the small end of the cable into the Pi and the large end into the battery. Make sure to recharge the battery when it runs low!

## Software ##

1. OS: Install the OS to the SD card (guide at https://www.raspberrypi.org/downloads/). Once installed, run the Pi and connect the Pi to your Wifi (you can connect it to your monitor over HDMI, then use a USB keyboard/mouse to control it)

2. Get the files: Add this software to the PI (I suggest making a folder in /home/pi, then cloning the repo into that folder. 
Example: Open a terminal with Ctrl+Alt+T. Enter "mkdir birds" to make a folder, "cd birds" to move into the folder, "sudo apt-get install git" to get git running, then "git clone https://github.com/Dernas/BirdPics.git"
to get this code. If you don't want to do all that, just download BirdSpotter.py, date.txt, and count.text to the Pi.)

3. Configure Drive: First, make a Google project to link to your Drive. See https://developers.google.com/drive/api/v3/quickstart/python?authuser=1
for instructions. Next, make a Drive folder to store the pics. Once you make the folder, replace the line
            "parents": ["15Xn3O4BaGPRjun25PWNGyAZIX6p8NLFz"]
			with
			"parents": ["YOUR_FOLDER_ID"] in BirdSpotter and ManualPicTaker.
To get the ID, go into the folder and look at the URL (something like https://drive.google.com/drive/u/0/folders/15Xn3O4BaGPRjun25PWNGyAZIX6p8NLFz")
You want the part after "folders/".

4. Version choice: If you want the IR version, skip to the next step. If you want the timer version, use "git checkout origin/timer"

5. Run on startup: There are many ways to run this process at startup. I used systemd (suggested by https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/).
Example: In a terminal, enter "sudo nano /lib/systemd/system/birds.service" to make a service file, then enter:
[Unit]
Description=Automatic Bird Pictures
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u BirdSpotter.py
WorkingDirectory=/home/pi/birds
StandardOutput=inherit
StandardError=inherit
Restart=always

[Install]
WantedBy=multi-user.target

After that, set permissions on your service ("sudo chmod 644 /lib/systemd/system/birds.service"), then tell the Pi to run it on startup ("sudo systemctl daemon-reload", "sudo systemctl enable sample.service"). After a reboot, the program should run every time you start the Pi!

6. (OPTIONAL) Easy manual pictures: To do this, you'll need a way to connect to your pi. I used SSH (https://www.raspberrypi.org/documentation/remote-access/ssh/). Once you're connected, you can use "sudo python3 /home/pi/birds/ManualPicTaker.py", or you can make it easy - use "sudo nano .bashrc", then add
"PATH=$PATH:/home/pi/.local/bin
alias bird=sudo python3 /home/pi/birds/ManualPicTaker.py"
The first command tells the Pi where to look for python, and the second one (reboot to make this work) lets you take a picture by typing "bird" as soon as you connect. Good luck!
