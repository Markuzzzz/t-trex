# t-trex
Python based quadruped robot powered by Raspberry Pi Zero 2 W

# nifty-inspirations
Nifty Projects - because simple solutions are hard to find!

## Description

t-trex for Raspberry PI is based on the Sunfounder Remote Control Crawling Robot by panerqiang@sunfounder.com, which was the main starting point of the Python code for this project. Especially the calculations related to kinematics of the legs was very helpful. Regis Hsu on his turn created an amazing 3D printed Quadruped frame which was also based on the Sunfounder project. t-trex is fundamentally built on the work of these two projects to jumpstart and extend with new features. The code written in C was ported to Python and fully refactored, because this programming language is focussed more on the ease of development. So easy to step in for beginners. And when Python is not fast enough (like compiled C code is), it can be combined with the low level C-language. Python is also very popular in the AI community and embedded solutions, resulting in massive amount of libraries to your disposal. Last but not least, Python is also very well supported by the Raspberry Pi ecosystem. 

## Features
- Fully Python 3 compatible

- Remote SSH over Wifi support

- PS4 Controller support (python-evdev)
    Gait Control
    Speed up/down movements
    Graceful Quit Program Hard Shutdown (mode 1 soft shutdown)
    Rumble support
    System report (mode 1 default stance)

- Different Gaits implemented
    Forward 
    Backward
    Left
    Right
    Stand (mode 1 head up)
    Sit (mode 1 head down)
    Head up/down

- PiJuice
    Monitoring by PiJuice for save shutdown on low battery voltage
    custom led usage for simple messages
    custom switch support for shutting down RPi OS

- Systemd bootable service (sequence)
    Logging to System Journal
    Automatic reconnect at startup
    Graceful Shutdown sequence on exception

To do
- Interruptable actions
- Advanced movements using analog joysticks
- AI Supervised Neural Net

## t-trex configuration

At the heart of this robot runs a RPi Zero W 2 as main cpu. Its controls 12 SG90 micro servo’s distributed over 4 legs using a I2C Servo PWM Pi (made by ABElectronics). To drive the power hungry micro servo’s, the power system consists of two separate power supplies to prevent voltage dips. One dedicated 1S LiPo @ 500 mAh for the RPi, fully managed by a PiJuice module on top of the RPi. Which is also able to charge the LiPo in place by USB or solar power source. The micro servo’s have their own power supply using a 2S LiPo @ 1300 mAh through a 5V buck converter for heavy duty action.

## Components
https://www.abelectronics.co.uk/p/72/servo-pwm-pi-zero
https://github.com/PiSupply/PiJuice
https://www.velleman.eu/products/view/?id=434062

## Installation
```bash
# Python3 setup
sudo apt install -y python3-dev
sudo apt install -y python3-smbus i2c-tools
sudo apt install -y python3-pil
sudo apt install -y python3-pip
sudo apt install -y python3-setuptools
sudo apt install -y python3-rpi.gpio

# Evdev 
sudo apt install python3-dev && sudo apt install python3-pip && sudo pip install evdev

# Pijuice Zero
sudo apt-get install pijuice-base

# Servo driver library
git clone https://github.com/abelectronicsuk/ABElectronics_Python_Libraries.git
sudo python3 setup.py install
```

## Additional Commands
```bash
# Increase Swap file 
df -Bm # check free space available
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change Swap size
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
sudo reboot now

# Prevent ssh ‘hang’ in terminal
Host ttrex.local
  HostName ttrex.local
  User markus
  ServerAliveInterval 10

# SSH connection set in terminal per server 
Sudo nano ~/.ssh/config
Host keepsdroppingme.com
   ServerAliveInterval 10

For killing it when it gets hang up, you can use the ssh escape character: ~.
'''
