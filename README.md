# Human Detection and Danger Zone Intrusion Detection System

This application named Human Detection and Danger Zone Intrusion Detection System will aid users in providing human detection and danger zone intrusion inside factories. It will notify alert messages sent to a host tablet if the human stays in the danger zone for a certain period of time.

<span style="color: red; ">**Please read "User Manual_v1.0.pdf" in detail.**</span>

**Hardware Setup:**

	NVIDIA Jetson Xavier NX
	7" 1024x600 capacitive touch monitor
	8MP camera (or equivalent) 
	Jetson-GPIO Buzzer
	Android Device (OS: Android 8-Oreo or greater, Preferably Tablet Device)

**Setup pre-requisites:**

	Jetpack 4.5.1 GA
	DeepStream SDK 6.0 EA
	GStreamer 1.14.1
	NVIDIA driver 465.31
	CUDA 11.1
	TensorRT 7.2.2
	OpenCV 4
	Jetson.GPIO 2.0.8
	Python 3.6
	Paho Mosquitto 1.5.1
	Shapely 1.5.9
	Matplotlib 2.1.1


## Installing Pre-requisites in Jetson Xavier NX:

**Jetpack SDK 4.5.1 GA:**

Download NVIDIA SDK Manager from https://developer.nvidia.com/embedded/jetpack. You will use this to install JetPack 4.5.1 GA (corresponding to L4T 32.5.1 release)

**DeepStream SDK 6.0 EA:**

 Download and install DeepStream SDK 6.0 EA.

 To download DeepStream SDK 6.0 EA from NVIDIA SDK, you should apply for early access. Get membership before you can download
 the installer including documentations.

**Gst-python:**

Should be already installed on Jetson.
If missing, install with the following steps:

	$ sudo apt-get install python3-pip
	$ sudo apt-get install python-gi-dev
	$ export GST_LIBS="-lgstreamer-1.0 -lgobject-2.0 -lglib-2.0"
	$ export GST_CFLAGS="-pthread -I/usr/include/gstreamer-1.0 -I/usr/include/glib-2.0 -I/usr/lib/x86_64-linux-gnu/glib-2.0/include"
	$ git clone https://github.com/GStreamer/gst-python.git
	$ cd gst-python
	$ git checkout 1a8f48a
	$ ./autogen.sh PYTHON=python3
	$ ./configure PYTHON=python3
	$ make
	$ sudo make install

If error encountered related to ./autogen.sh, please try below;

	$ export GIT_SSL_NO_VERIFY=1

**Mosquitto MQTT Broker:**

	$ sudo apt-get update
	$ sudo apt-get install mosquitto mosquitto-clients

**Shapely:**

	$ pip3 install Shapely

If error encountered related to geos_c, install libgeos-dev

	$ sudo apt-get install libgeos-dev

**Matplotlib:**

	$ sudo apt-get update
	$ sudo apt-get install python3-matplotlib

**MQTT Client:**

	$ pip3 install paho-mqtt


## Running the Application

Human Detection and Danger Zone Intrusion Detection is configured to work with DeepStream SDK 6.0 EA. 

1. Prepare the dangerzone App  
```
$ cd ~/Downloads
$ git clone https://github.com/MACNICA-CLAVIS-NV/dangerzone.git  
```

2. Copy the dangerzone App

```
$ cd /opt/nvidia/deepstream/deepstream-6.0/sources/
$ sudo mkdir deepstream_python_apps
$ cd deepstream_python_apps/
$ sudo mkdir apps
$ sudo cp -r ~/Downloads/dangerzone/hddzids ./apps/
$ cd ./apps/
$ sudo chmod -R 777 ./hddzids  
```

3. Confirm the Deepstream lib declaration inside ./hddzids/dist/common/is_aarch_64.py  
```
$ gedit ./hddzids/dist/common/is_aarch_64.py
```
4. Edit the MOBILE_HOST constant in ./hddzids/dist/common/constants.py with the IP Address of the Jetson device.  
Ex. MOBILE_HOST = “192.168.1.17”

4. Run the program.  
```
$ cd ./hddzids/dist
$ python3 main.py
```
## Using the Application

1. Run 'python3 main.py'
2. Wait for camera stream to show
3. While streaming, drag and drop to select the initial area for Bird's Eye view calibration.
4. Corners are adjustable before saving.
5. Press 's' to save the selected area for Bird's Eye view calibration.
6. Next, drag and drop to select the initial area for Danger Zone calibration.
7. Corners are adjustable before saving.
8. Press 's' to save the selected area for Danger Zone calibration.
9. Press 'q' to continue to main process of detection and tracking.

**Note:**  
a. Calibration window will only display when there’s no existing calibration beforehand.  
	b. You can retry to do the calibration by deleting the calibration file save in ./hddzids/data/calibration.txt
