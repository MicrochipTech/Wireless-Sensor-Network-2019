# Microchip Wireless Sensor Network -2019
Create a Wi-Fi/ MiWi (15.4) / LoRaWAN wireless sensor network to monitor the temperatures covering a wide area like a hotel or a plant. 

Case study: Classrooms temperature monitoring during Microchip MASTERS conference held at JW Marriot desert ridge, AZ

[View the demo (Live only during MASTERS conference)](http://demo.microchip.com/WSN/masters/ "view the demo (Live only during MASTERS conference)")

## Features

- Monitors sensor data (temperature, battery level and RSSI)
- Covers 34-35 locations over a vast area of approx. 1 km2
- Secure communication with AWS IoT for Wi-Fi
- Device independent web interface to easily view data
- Display of MiWi Mesh topology in WSN Monitor GUI
- Data logging to csv file
- Battery operated devices
- Showcase different technologies tackling the same task


   **Smart Secure Connected**
![](https://www.microchip.com/ResourcePackages/Microchip/assets/dist/images/logo.png)

![](https://img.shields.io/github/issues/MicrochipTech/Wireless-Sensor-Network.svg) ![](
https://img.shields.io/github/forks/MicrochipTech/Wireless-Sensor-Network.svg) ![](
https://img.shields.io/github/stars/MicrochipTech/Wireless-Sensor-Network.svg) 


- [Microchip Wireless Sensor Network](#microchip-wireless-sensor-network)
  * [Features](#features)
- [Overview](#overview)
  * [Technologies used](#technologies-used)
    + [Web page Front End](#web-page-front-end)
    + [Data endpoint API](#data-endpoint-api)
    + [Server hosting](#server-hosting)
    + [Cloud IoT core](#cloud-iot-core)
    + [End point](#end-point)
  * [Block diagram](#block-diagram)
- [Cloud](#cloud)
  * [AWS](#aws)
    + [AWS EC2](#aws-ec2)
  * [TTN](#ttn)
  * [Server](#server)
    + [Flask data application](#flask-data-application)
      - [Node location dictionary](#node-location-dictionary)
      - [Data logging](#data-logging)
      - [MQTT subscriber](#mqtt-subscriber)
        * [AWS IoT MQTT client](#aws-iot-mqtt-client)
        * [TTN IoT MQQTT client](#ttn-iot-mqqtt-client)
    + [HTML website](#html-website)
- [End nodes](#end-nodes)
  * [Wi-Fi](#wi-fi)
    + [Demo summary](#demo-summary)
    + [Hardware used:](#hardware-used-)
    + [Firmware update](#firmware-update)
    + [Software requirements](#software-requirements)
    + [Steps to get up and running](#steps-to-get-up-and-running)
    + [Provisioning ECC608 device and WINC1500 to your AWS account](#provisioning-ecc608-device-and-winc1500-to-your-aws-account)
    + [Programming SAML21 to connect and publish to AWS IoT](#programming-saml21-to-connect-and-publish-to-aws-iot)
      - [AP configuration](#ap-configuration)
      - [Node name](#node-name)
      - [sleep code and duration](#sleep-code-and-duration)
      - [MQTT client ID](#mqtt-client-id)
      - [Running the code](#running-the-code)
  * [LoRaWAN](#lorawan)
    + [Introduction](#introduction)
    + [Advantages of LoRaWAN](#advantages-of-lorawan)
    + [Demo Introduction](#demo-introduction)
    + [Hardware](#hardware-required)
    + [Software](#software)
    + [Step by Step Procedure to replicate Demo](#step-by-step-procedure-to-replicate-demo)
    + [Registration Links](#registration-links)
  * [MiWi](#miwi)



# Overview

At MASTERS 2019, we monitored temperatures conference-wide using 3 different networks simultaneously reporting into a single, easily accessible dashboard hosted online to view the information of 34 locations. In addition, for LoRa implementation we added a golf course node that is placed outside of the hotel to showcase LoRa long range capabilities.

The system is compromised mainly of two parts:
- Cloud side code
- Local infrastructure and end nodes 

The same demo and functionality can be achieved using any of the 3 technologies. However, each technology has its own strengths and drawbacks. We provide this explanation and the supporting code to aid microchip customers choose the technology that suits their application best. 

Note: the code here is provided AS IS and was not tested for production quality. It has some knowm issues in the cloud section that we mention later on. You are fully responsible to test and adapt the code on your own system. 

## Technologies used

### Web page Front End
The user needs a portal to view the data. To make a platform independent view that doesn't require installation or a password we choose to display the data on a **HTML + JavaScript** webpage. 

The webpage is only a tool that retrieve the data from a data end point, it can be replaced by a phone application or added to a per user view in a final product. 

### Data endpoint API 
To make our application modular and independent on the Front End implementation, whether it's a website or a mobile application. we decided to implement a RESTful API  using **Flask**

The data is returned as JSON object from the endpoint and can be viewed [here](http://demo2.microchip.com/WSN/Data/Wi-Fi/ "here").

### Server hosting
For the purpose of this demo, we used **Amazon EC2** ubuntu virtual machine instance (since we were already using AWS IoT core) to easily manage all of our services on the same interface..

However, the same could be achieved with DigitalOcean as an alternative. In a commercial real world application, you will probably have your own server and this step is unnccessary.

### Cloud IoT core
For the sake of this demo, when using **Wi-Fi or 802.15.4 (MiWi)** we decided to go with **Amazon AWS IoT core**.  

When using **LoRa & LoRaWAN**, you have to register and use one of the LoRaWAN service providers like **The Things Network (TTN) **or senet. 

For the purpose of this demo we went with TTN.  We also had success with converting this demo to senet in India but this is outside of the scope of this page.


### End point
The design and technology used in end nodes can be either:
- Wi-Fi (IEEE 802.11) 
- MiWi (microchip proprietory IEEE 802.15.4)
- LoRa (proprietory Sub-GHz)

When choosing end nodes user needs to consider:
1. Power budget.
2. Available Infrastructure.
3. Required coverage range.
4. Running cost.
5. Secuirty.
6. Deployment effort.

each of these points are discussed in the end node sections below. 

## Block diagram
![](https://i.imgur.com/BMSXe9Y.jpg)

The diagram above summarize the system. End nodes are in sleep mode until a given time where it wakes up, sends the data to the gateway and then goes back to sleep. 

LoRa and MiWi need a dedicated gateway to bridge from LoRa/MiWi to Wi-Fi before sending the data to the cloud. Wi-Fi has an advantage that it doesn't need a dedicated Gateway if there is Wi-Fi coverage already which is the case for our Hotel location.

The data is sent to Cloud servicer provider. AWS IoT for Wi-Fi and MiWi and TTN for LoRa. Our Flask application will then get the data and provide a modular Data end point that our webpage can present.  The flask application and the web interface both colocate on our AWS EC2 instance. 

The user then can access our web page from any device anywhere he wants.

# Cloud
In this section we discuss how to setup the cloud portion of the demo.
## AWS
we utilize two services from AWS in this demo, AWS EC2 as a server hosting platform. and AWS IoT for Wi-Fi and MiWi end nodes MQTT broker.
### AWS EC2
To host your server you will have to create a virtual machine EC2 instance before you deploy apache into it.  The process is easy and straight forward once you have your AWS account ready. 

For a step by step guide please follow the amazon guide [here](https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html "here").

For our demo we went with free this instance type:
**ubuntu Server 16.04 LTS  free tier** 
(upgraded to medium during conference to accomodate demand)

At security setting, allow access to inbound & outbound HTTP, HTTPS and SSH traffic. you can also adjust the security setting to your liking.  Also, please keep the private key to access the instance safe so you can push your data in it and control the server. 

To access your server, follow the guides available in amazon website [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html "here"). 
###AWS IoT
Wi-Fi nodes will need to connect to AWS IoT core to send sensor data over MQTT. 

To set up AWS IoT Cloud, you can follow the user guide of AWS Zero Touch Provisioing Kit project (From Section 2 Software Installation to Section 5 AWS IoT Just-In-Time Registration Setup )
User needs to create Lambda function, AWS IoT Rule and IAM role for AWS provision.

AWS Zero Touch Provisioing Kit is a project about provisioning the Zero Touch Secure Provisioning Kit to connect and communicate with the Amazon Web Services (AWS) IoT service.
The user guide of AWS Zero Touch Provisioing Kit project can be found from below: 
http://microchipdeveloper.com/iot:ztpk
## TTN
## Server
once you have your EC2 instance up and running after following the steps above, you will  need to install apache and point it to host our web page and the flask application.

EC2 instance already comes with python, make sure you git pip as we will need it later on.
`$ sudo apt-get update`
and
`sudo apt-get install python3-pip`


### Flask data application
First, install flask on your EC2 instance:
`$ pip3 install Flask`

copy the "Server/wsn_server.py" file to the EC2 instance. 

Now let's describe parts of the code that you will want to modify and adapt to your application:
#### Node location dictionary
you will find dictionaries named "USMastersNodeLocation" and "IndiaMastersNodeLocation".. the reason is, we wanted our boards to be reused for multiple demo location without changing the code on the board, so we give each node a number and use this dictionary to map the node to the room it's put inside. 

for example, Node4 during US masters on "Desert Suite 4". then we shipped the same node to india and put it on "Dominion" room. this way the same node, with the same code can be used for different location just by changing the flask application without the need to physicall program the device. 

**Updating the code physically on the board is not always convenient in the field. We encourage you to think of methods like this and plan ahead to avoid updating the board FW.**

```python
#our Rooms database
USMastersNodeLocation = {
    "Node1": "Desert Suite 1",
    "Node2": "Desert Suite 2",
    "Node3": "Desert Suite 3",
    "Node4": "Desert Suite 4",
    "Node5": "Desert Suite 5",
    "Node6": "Desert Suite 6",
    "Node7": "Desert Suite 7",
    "Node8": "Desert Suite 8",
    "Node9": "Pinnacle Peak 1",
    "Node10": "Pinnacle Peak 2",
    "Node11": "Pinnacle Peak 3",
    "Node12": "Wildflower A",
    "Node13": "Wildflower B",
    "Node14": "Wildflower C",
    "Node15": "Grand Canyon 1",
    "Node16": "Grand Canyon 2",
    "Node17": "Grand Canyon 3",
    "Node18": "Grand Canyon 4",
    "Node19": "Grand Canyon 5",
    "Node20": "Grand Canyon 9",
    "Node21": "Grand Canyon 10",
    "Node22": "Grand Canyon 11",
    "Node23": "Grand Canyon 12",
    "Node24": "Grand Sonoran A",
    "Node25": "Grand Sonoran B",
    "Node26": "Grand Sonoran C",
    "Node27": "Grand Sonoran D",
    "Node28": "Grand Sonoran H",
    "Node29": "Grand Sonoran I",
    "Node30": "Grand Sonoran J",
    "Node31": "Grand Sonoran K",
    "Node32": "ATE / Grand Canyon 6",
    "Node33": "Cyber Cafe / Grand Sonoran G",
    "Node34": "Grand Saguaro East/West",
    "Node35": "Golf course"
}
```
#### Data logging
we store the data we receive on a CSV file. the file location and name is specified on line 141-143.

```python
###################################
###### Files to store data ########
###################################
wifiFile = open('/home/c43071/WSN/wifiData.csv', 'a')  
miwiFile = open('/home/c43071/WSN/miwiData.csv', 'a') 
loraFile = open('/home/c43071/WSN/loraData.csv', 'a') 
WiFiWriter = csv.writer(wifiFile)
MiWiWriter = csv.writer(miwiFile)
LoRaWriter = csv.writer(loraFile)
```

#### MQTT subscriber
To get notifications from end node, the application need to subscribe to AWS IoT core and TTN servers (or any server you choose)

##### AWS IoT MQTT client
we used the publickly provided pythond code for AWS IoT. to use it, please go to amazon github repo [here](https://github.com/aws/aws-iot-device-sdk-python "here").

our code  can be used as is if you replace the certificates path with your certificate path. 
```python
# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("WSNClientID")

# For TLS mutual authentication with TLS ALPN extension
myMQTTClient.configureEndpoint("a3adakhi3icyv9.iot.us-west-2.amazonaws.com", 443)
myMQTTClient.configureCredentials("/home/c43071/WSN/VeriSign.pem", "/home/c43071/WSN/WSN_BE_private.pem", "/home/c43071/WSN/WSN_BE_certificate.pem")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
myMQTTClient.connect()
```
The code expect the topics to be known and one topic per technology. the user can use different topics with different access if he wish.
```python
myMQTTClient.subscribe("/Microchip/WSN_Demo/WiFi", 1, WiFiCallback)
myMQTTClient.subscribe("/Microchip/WSN_Demo/MiWi", 1, MiWiCallback)
```

The code expects a json object with the format:
` {'nodeID': "Node1", 'Battery': "4.99V", 'Temperature': 81.46, 'RSSI': -55}`

##### TTN IoT MQQTT client
The thing network  doesn't require mutual authentication or certificates to connect like AWS, instead they rely on username and password. Hence we show case how to connect to their server using the "flask_mqtt" package.
```python
from flask_mqtt import Mqtt

app.config['MQTT_BROKER_URL'] = 'us-west.thethings.network'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'jwmarriottdesertridge'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
mqtt = Mqtt(app)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print ("MQTT connected!!!\r\n")
    mqtt.subscribe('jwmarriottdesertridge/devices/+/up')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
```
You will notice that the message payload for LoRA is a little bit different than Wi-Fi and MiWi, this is due to TTN gateway adding some info to the end node payload and due to us trying to minimize the pay load as much as possible to decrease power used and increase effeciency. please refer to the LoRa section below. 

###Apache

There are plethora of apache tutorials and content out there, we just mention the deviations here. 

First, get apache and wsgi for flask:
`sudo apt-get install apache2 libapache2-mod-wsgi-py3`

Create a wsgi file:
`vi wsn_demo.wsgi`

put this in the above file:
```python

import sys
sys.path.insert(0, '/var/www/html/WSN')
```

Create a symlink so that the project directory appears in /var/www/html:
`$ sudo ln -sT ~/WSN /var/www/html/WSN`

Enable wsgi:
`sudo a2enmod wsgi`

Configure apache (you will need to sudo to edit the file)
`$ sudo vi /etc/apache2/sites-enabled/000-default.conf`

we will create 2 virtual host, one for the data end point and one for out website.

Line 9 & 49 below indicate your website name. 
Line 14 have your wsgi file location. 

Paste this in "000-default.conf" after making your host modifications as mentioned above:
```html
<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName demo2.microchip.com

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        WSGIDaemonProcess WSN threads=5
        WSGIScriptAlias / /var/www/html/WSN/wsn_demo.wsgi

        <Directory WSN>
                WSGIProcessGroup WSN
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
        </Directory>

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>


<VirtualHost *:80>
        # The ServerName directive sets the request scheme, hostname and port that
        # the server uses to identify itself. This is used when creating
        # redirection URLs. In the context of virtual hosts, the ServerName
        # specifies what hostname must appear in the request's Host: header to
        # match this virtual host. For the default virtual host (this file) this
        # value is not decisive as it is used as a last resort host regardless.
        # However, you must set it for any further virtual host explicitly.
        ServerName demo.microchip.com

        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/Masters

        DirectoryIndex index.html

        # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
        # error, crit, alert, emerg.
        # It is also possible to configure the loglevel for particular
        # modules, e.g.
        #LogLevel info ssl:warn

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        # For most configuration files from conf-available/, which are
        # enabled or disabled at a global level, it is possible to
        # include a line for only one particular virtual host. For example the
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
</VirtualHost>

```
Restart the Server:
`$ sudo apachectl restart`

Now you need to make a dns entry that will map from "demo.microchip.com" & "demo2.microchip.com" to the public IP address of the EC2 instance. 

once that is done, go ahead and view your data in a link similar to:
http://demo2.microchip.com/WSN/Data/LoRa/

and the website will be similr to: (depending on how you configured apache and where you put your HTML files):
http://demo.microchip.com/WSN/Masters/

### HTML website 
when you inspect the HTML pages we provide at "Server\US IoT Network\IoT Network"

thee important file is "scripts.js" which go and read the data from our data endpoints above. 

The rest is just HTML files containing a table and SVG files for the location map. 

# End nodes
In this section we describe the necessary steps to start sending sensor data to the cloud using each respective technology. 

## Wi-Fi
Reasons you may want to choose Wi-Fi as your end node:

**Advantages of WiFi **
1. Non-Prevasive: Wi-Fi infrastructe is already availabe in many place (hotels, malls, airports ..etc) making the system easy to deploy and doesn't require any external gateways.
2. Speed: sensor network is not usually a high bandwidth demanding task. but if you want to support features like in field OTA or high bandwidth then Wi-Fi is your best option. 
3. Payload size: Other networks like LoRa puts a limit on your payload size. 
4. Cost: No gateway cost required, no need to pay for usage subscription.
5. Power cord connected devices.

Reasons that makes Wi-Fi a less ideal options:
1. If there is no deployed Wi-Fi infrastructre in the area or a plan to do so.
2. If the application is battery powered AND it require very frequent connection (e.g each 5 min) .. Wi-Fi on battery is viable for applications with low volume infrequient connection. 

### Demo summary
The Wi-Fi board sleeps for a period of time that is configurable. When it wakes up, it checks to see if the sensor reading has changed since last reported to the cloud. If it chooses to update the reading, it will connect to the AP usning the Wi-Fi module and authenticate with AWS cloud using the Crypto-Auth chip (ECC508) and send the updated values. 

The board need to be provisined first time only before it can be used, we go through this below.

### Hardware used:
For The demo we used the IoT sensor bord which contain an MCU (SAML21) and a Microchip Wi-Fi module (ATWINC1500) and other sensors. 

For more info on the HW please go to this page [Here](https://github.com/MicrochipTech/aws-iot-winc1500-secure-wifi-board-included-source-files/wiki/Hardware-Overview "Here"). 

The board is not available for purchase at the moment @microchip direct. it was distributed to MASTERS conference attendees for Free and will be added later for purchase option.  In the mean time, you can do the same using the [AWS Zero touch kit](https://www.microchip.com/promo/zero-touch-secure-provisioning-kit-forAWSIoT "AWS Zero touch kit").

### Firmware update
To flash firmware to the board, please go through the options [Here](https://github.com/MicrochipTech/aws-iot-winc1500-secure-wifi-board-included-source-files/wiki/Firmware-Overview "Here"). 

### Software requirements
Please head over to [this page](https://github.com/MicrochipTech/aws-iot-winc1500-secure-wifi-board-included-source-files/wiki/Software-Installation "this page") to install the necessary tools. 

### Steps to get up and running
Now. if you want to use Wi-Fi the steps are like this:
-  get the cloud section done first. Your AWS account should be ready so the node can connect to it. 
- Provision the WINC1500 and the ECCx08 device to connect to your AWS account. 
- Flash the code to the MCU (SAML21) that will actually connect to AWS and start publishing MQTT messages. 

The first step is covered in the cloud section. you can also go ahead to aws.amazon.com and follow their guide incase they changed the steps.  we will cover the 2nd and 3rd steps here.
### Provisioning ECC608 device and WINC1500 to your AWS account
The ECC608 device is the valut that protect your device identity and authenticate with the AWS cloud. 

To provision your ECC608 device, please follow the steps [Here](https://github.com/MicrochipTech/aws-iot-winc1500-secure-wifi-board-included-source-files/wiki/AWS-Provision-Setup "Here").

Once you're done with the steps above, your ECC608 is provisioned. The remaining part is to Store the device certificate on the WINC1500.

This can be done programatically from the application side by calling:
`m2m_ssl_send_certs_to_winc`
The above is suitable for production. an alternative is by using the tool in [this guide](http://ww1.microchip.com/downloads/en/DeviceDoc/50002599A.pdf "this guide").


### Programming SAML21 to connect and publish to AWS IoT
Once both the ECC608 and WINC1500 are provisioned. You can finally flash the board with the real application. 

The application example on the Wi-Fi folder contain reference code to do so. 
![](https://i.imgur.com/2CrLj2x.png)

There are to projects there:
- ECC608_provisioning: contains code that help put WINC1500 in FW update mode and provision the ECC608. you don't need to use this project if you have followed the steps above. Feel free to explore the main.c if you wish.
- IoT_sensor_board_AWS_MQTT: This is the project that do the actual MQTT publishing to the cloud, here we describe the main points.

#### AP configuration
You can change the AP SSID and password that you want to connect to on Lines 61/63 on main.h
![](https://i.imgur.com/wt6S7p9.png)
#### Node name
The node name is on Line 73, on main.h
![](https://i.imgur.com/KRuEgoU.png)
#### sleep code and duration
The SAML21 goes to sleep and wakes up on RTC interrupt. 
The MCU will go to sleep upon a call to:
`system_sleep();`
and wakes up when the RTC interrupt is received. To control the duration for RTC interrupt, configure the count in the function "configure_rtc_count" on rtc.c,, the sleep duration depend on how often you want to refresh the data and your power budget.

![](https://i.imgur.com/Io9RAUA.png)

#### MQTT client ID
You have to enter the MQTT client ID to be similar to the subject ID in your device certificate. enter the client ID into the "gAwsMqttClientId" variable in Line 95 of "winc15x0.c"

![](https://i.imgur.com/NJzcDnj.png)

#### Running the code
That's pretty much it, now go to main.c file, read the main function and get familiar with it and when you're ready, build and Flash the SAML21 with the code. 

If you are logged into the AWS test consle ans subscribing to the Wi-Fi topic mentioned above (/Microchip/WSN_Demo/WiFi) you should see a new message received once the board runs.
## LoRaWAN

### Introduction
LoRa stands for Long Range. LoRaWAN stands for Long Range Wide Area Networks. LoRaWAN is the network on which LoRa operates. LoRaWAN is a media access control (MAC) layer protocol but mainly is a network layer protocol for managing communication between LPWAN gateways and end-node devices as a routing protocol, maintained by the LoRa Alliance. Some of the  applications that can be accomplished using LoRa are Smart parking and vehicle management, Facilities and infrastructure management, Fire detection and management, Waste management, Home automation for IoT enables smart appliances, Smart farming and livestock management, Temperature and moisture monitoring, Water level sensors and irrigation control.

### Advantages of LoRaWAN
- Long battery life due to low power consumption
- Low cost implementation due to low cost hardware and unlicensed spectrum
- Long range coverage and in-building penetration
- Secure Network
- Scalable network to support future upgrades
- Ease of access and connectivity to the cloud applications
- Remote management and control access

### Demo Introduction
Temperature of rooms spread across a huge resort was monitored using the LoRa.
A typical LoRa Application can be developed by having 4 components
End Device, Gateway, Network Server and Application Server.
End Device with Temperature sensor (running on batteries) was used to demonstrate the advantages of LoRaWAN such as low power, secure and long range.
Users who are new to developing applications using LoRaWAN can find overview of LoRaWAN System Architecture [here](https://www.thethingsnetwork.org/docs/lorawan/ "here"). 


### Hardware
- End Device used for this demo [SAMR34 Xplained Pro Evaluation Kit](https://www.microchip.com/DevelopmentTools/ProductDetails/dm320111 "SAMR34 Xplained Pro Evaluation Kit") - 1
- Gateway used was the [The Things Gateway](http://thethingsproducts.com/#the-things-product-buy "The Things Gateway")
- Internet Connectivity
- micro USB Cable - 1
- Battery Pack with 3 AAA 1.5V batteries to Power the end device using J100 5V0_IN and GND on the end device - 1
- Female-Female Jumper wire shorting PA15 to GND - 1
- [I/O1 Xplained Pro Extension kit](https://www.microchip.com/DevelopmentTools/ProductDetails/ATIO1-XPRO "I/O1 Xplained Pro Extension kit") (Temperature Sensor) - 1

### Software
- Network Server used was the [The Things Network](https://console.thethingsnetwork.org/ "The Things Network")
- Application Server used was Flask Application, python script subscribed to The Things Network - Network Server
- [Atmel Studio 7 ](https://www.microchip.com/mplab/avr-support/atmel-studio-7 "Atmel Studio 7 ")and above IDE
- ASF 3.47 and above

### Step by Step Procedure to replicate Demo
1. Ensure the Gateway is connected to The Things Network Server - Steps mentioned [here](https://www.thethingsnetwork.org/docs/gateways/gateway/ "here")
2. Once the Gateway is online, "Create an Application" followed by "Create a new device" 
section for registering the application and end device to TTN
3. Once the end device is created in The Things Network Console and necessary code changes have been made in the Application source code for devEUI and AppEUI. We will be using OTAA method of join for our Application.
4. To enable Battery Voltage Measurement, ensure PA15 is shorted to GND.  I/O Jumper and MCU Jumper should be bypassmode
5.  Connect the ATSAMR34-XPRO to PC using a micro usb cable  through EDBG Power Supply. ATSAMR34-XPRO will enumerate as a COM Port. Using a Terminal Application @ baudrate 115200, Data - 8 bit, Parity - None, Stop - 1 bit and Flow control - None settings will enable a user to monitor information from the Firmware example
6. Open the project - APPS_ENDDEVICE_DEMO using Atmel Studio
configure the devEUI, appKey and AppEUI using the conf_app.h file available in following directory - /src/config
![](https://i.imgur.com/wH7bvSo.png?1)
7. If Application developed is using NA/AU bands, use can choose a subband the Gateway is listening on. As NA/AU band allow upto 64 uplink channels. Popular inexpensive gateways here on only 8 channels, hence a subband choice is required.
The Things Gateway listens on subband - 2 for NA otherwise called US902 as per the LoRaWAN regional parameters. For the demo we have used OTAA (over the air activation) join methodology in LoRaWAN 
8. Program the demo using "Start Without Debugging" Option on Atmel Studio.  After programming the demo, the End Device (ATSAMR34-XPRO) will try to join the LoRaWAN Network Server (The Things Network). If the Gateway is online and connected to the Things Network Server, join request will result in a immediate join acceptance.
![](https://i.imgur.com/ouco0IA.png)
9. TTN has a feature called TTN Functions which allows users to change bytes, sent over The Things Network, to human readable fields.
To add the API for this demo, go to Applications --> XXXX --> Payload Formats
XXXX denotes users Application Name
	Go to Decoder Section and save the below decoder function
	
	Decoder Function:
	--------------------------------------
		function Decoder(bytes, port) {
		var length = bytes.length;
		if(length == 6){
		var temperature = (bytes[0] <<8) | bytes[1];
		var battery = (bytes[2] <<8) | bytes[3];
		battery = battery/100 + "V";
		var time = bytes[4] + ":" + ('0' + bytes[5].toString(10)).slice(-2);
		return{
		"temperature": temperature /100,
		"battery": battery /// 100, // this operation now is done in earlier step
		"time": time
		};
		}else
		{
		var result = "";
		for (var i = 0; i < length; i++) {
		result += String.fromCharCode(parseInt(bytes[i]));
		}
		return {
		"msg": result,
		};
		}
		}
10.  After configuring the decoder and programming the board with the Application Source code. The App data should start appearing in terminal window and on the Things Network Console
![](https://i.imgur.com/SpqHM6k.png)

Subsequent sensor transmissions happen every 15 mins

11. Application data on cosole can be controlled and monitored via Application Server Integration. The things network provides this service
![](https://i.imgur.com/JOOUuns.png)
 
### Registration Links
- [The Things Gateway Registration](https://www.thethingsnetwork.org/docs/gateways/gateway/ "**The Things Gateway Registration**")
- [Application Registration](https://www.thethingsnetwork.org/docs/applications/add.html "Application Registration")
- [Device Registration ](https://www.thethingsnetwork.org/docs/devices/registration.html "Device Registration ")


## MiWi

**Introduction**
MiWi stands for Microchip Wireless. MiWi is a proprietary wireless protocols designed by Microchip Technology that use small, low-power digital radios based on the IEEE 802.15.4 standard for wireless personal area networks (WPANs). It is designed for low data transmission rates and short distance, cost constrained networks, such as industrial monitoring and control, home and building automation, remote control, low-power wireless sensors, lighting control and automated meter reading.
MiWi protocol supports three network topologies
- Peer to Peer (P2P)
- Star
- Mesh

**Advantages of MiWi**
- Long battery life due to low power consumption
- Low cost implementation due to low cost hardware and unlicensed spectrum
- Long range coverage and in-building penetration when using Sub GHz Radios
- Secure Network
- Over the Air Upgrade Firmware Upgrade
- Customizable
- Quick Time to Market
- Lower Memory Footprint 
- No licensing Fee


**Demo Introduction**
Temperature of rooms spread across a huge resort was monitored using the MiWi Mesh Network Topology.

![](https://i.imgur.com/NaCLAsK.png)

A typical MiWi Mesh Application can be developed by having 3 components.
- Pan Coordinator
    - Starts the network
    - Assigns and maintains the coordinators and its end-devices addresses
    - Behaves as coordinator for routing frames
    - Controls the devices which can be included into the network through commissioning
- Coordinator
    - Supports routing of frames within the network
    - Stores the commissioning information from PAN coordinator and allows only the commissioned devices to participate in the network
    - Maintains its end-devices and their addresses
    - Maintains data for sleeping end-devices 
- End Device
	- Joins to network though available coordinators
	- Supports Rx-On end-device and Sleeping end-device for battery operated devices
	- Supports dynamic switching between Rx-On to Sleeping end-device and vice versa

Pan Coordinator & Coordinator are of FFD (Full Function Device) type and are capable of routing the packets
End Devices can be FFD(Full Function Device) / RFD(Reduced Function Device) type. RFD end devices were used for the purpose of this demo because of the capability to go to sleep. End Device with Temperature sensor (running on batteries) was used to demonstrate the advantages of MiWi Mesh network such as low power, self healing etc

The PAN-Coordinator Node is connected to SAMA5D2 XPRO board and it has a WILC3000 for Wi-Fi (Internet) Connectivity. This combination of devices is referred to as MiWi Bridge in this demo.
![](https://i.imgur.com/SXM9qwM.png)
The Routers and End-Devices send periodic data to PAN-Coordinator. The SAMA5D2 reads the data from PAN-Coordinator and send the same to AWS EC2 instance.
The AWS EC2 instance sends the received data to WSN Monitor Tool and to the Webserver. WSN Monitor tool depicts the mesh topology formed from the data received from router, sensor nodes and PAN-Coordinator. WSN Monitor can also be used to monitor the MiWi Network.

**Hardware**
- Pan Coordinator ([ATSAMA5D2-Xplained Ultra board](https://www.microchip.com/Developmenttools/ProductDetails/ATSAMA5D2C-XULT)+ [ATWILC1000 SD board](https://www.microchip.com/DevelopmentTools/ProductDetails/PartNO/AC164158) + [SAM R30M Xplained Pro](https://www.microchip.com/DevelopmentTools/ProductDetails/ac164159))
- Coordinator ([SAM R30M Xplained Pro](https://www.microchip.com/DevelopmentTools/ProductDetails/ac164159))
- End Device ([SAMR30 Sensor Board]
- Internet 

**Software**
- Atmel Stdio 7 + (IDE)
- ASF 3.47+
- Pan Coordinator Application Project (/MiWi/SAMR30/PAN_CORD_MOD)
- Coordinator Application Project (/MiWi/SAMR30/CORD_MOD1)
- End Device Application Project(/MiWi/SAMR30/SENSOR_MOD1)
- BuildRoot image
- Linux Kernel 4.14.73 used from Linux4sam_6.0
- WILC1000 Driver and firmware 15.02 release
- AWS Cloud Server account
- WSN monitor Tool 2.2.1

**AT91SAMA5D27 on Linux**
- Linux4Sam_6.0 package with kernel 4.14.73 used to generate the zImage, device tree file by compiled on GCC compiler 7.3.0.
- BuildRoot is built with required python2.7 modules, which will be used in TCP application.

**ATWILC3000 Modules & Firmware**
- WILC driver 15.02 version compiled against Kernel 4.14.73 and added in the `$ /root` of the Buildroot package. Firmware is added in `$ /lib/firmware/mchp`.
- After the SAMA5D2 device kernel boot up, in root files system "mchp" folder will be available.

**AWS Cloud EC2 Instance Services**
-	Using AWS, create an EC2 service with AMI free-tier instance.
-	This EC2 instance will provide the public and private IP’s to communicate with VPC Linux machine.
-	In this AMI required applications are already installed to run our python based application.
-	Using SSH application with private key provide by AWS cloud we open the VPC Linux terminal.
-	This Linux terminal will be used to run any application developed on python.

**WSN Monitor Tool**
- The tool used to monitor and control the MiWi network. Tool is having two options to connect with network such as Serial port or TCP client.
- In this demo, TCP client option is used to connect with AWS Cloud TCP server.

**Step by Step Procedure to replicate MiWi Demo**
**SAMA5D2 Linux Setup**
1. Demo package contains the $ sdcard.img and $ emmc-usb.qml scripts.
2. Connect the FTDI cable to the Debug connector (J1).
    - Note: Do not use J14 connector to receive debug messages.
3. Connect a USB cable to J23 port to flash the image.
4. Close the jumper JP9, press the reset button and open the jumper.
5. Navigate to /MiWi/SAMA5D2_image folder in command prompt.
6. Excute the update.bat script available at /MiWi/SAMA5D2_image folder. This will install the Demo Image on the SAMA5D2 Xplained eMMC.
7. Image downloading will be completed in one or two minitus in to SAMA5D2 Xplained eMMC flash. Press any key to conitnue when prompted.
8. Once Flashing completed, reboot the board and to initialize the kernel and mount root files system.

**Bring up WiFi interface and WiFi Connection**
1. After the target board boot up, root file system will be mounted.
2. Login in to target system using `$ root` as user name.
3. Target board root files system path `$/root/mchp/` folder contain the WILC3000 driver module.
4. In this `$/root/mchp` folder contains the WILC3000 driver module.
5. WILC3000 firmware is loaded in file path, `$ /lib/firmwae/mchp/wilc1000_wifi_firmware.bin`
6. WILC3000 15.02 driver and firmware release version is used.
7. Copy the shell script (S99MiWiDemo.sh) and tcp client python appication (miwi_network_client_masters.py) from /MiWi/Scripts/SAMA5D2/ in a USB drive to root folder in SAMA5D2.
8. Using the `$ vi` editor modify script for Router credentials.
9. Modify the SSID and router password psk as the router configuration.
10.After updataing the SSID and psk in S99MiWiDemo.sh, copy the script to /etc/init.d directory
11. In miwi_network_client_masters.py, update SERVER_IP  with public IP address of ec2 instance.
12. Restart SAMA5D2 board, After bootup, WILC3000 will be connected to Router, show the status of the WiFi connection and then it will execute the miwi_network_client_masters.py application

**AWS Cloud EC2 Instance Setup**
We utilize EC2 (Amazon Elastic Compute Cloud) services for this demo. EC2 instance host the two TCP servers for MiWi network bridge and WSN monitor tool.
**AWS EC2 Instance**
To host the python server, requires AMI Linux virtual machine. Amazon EC2 instance will provide the virtual Linux machine. The process is easy and straight forward once you have your AWS account ready.

- For a step by step guide please follow the amazon guide.
     - https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html
- To access the server follow the Amazon user guide.
     - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html
- Copy the TCP Server application (miwi_wsn_server_4.py) available at /MiWi/Scripts/AWS/ folder to EC2 instance virtual machine.
- To update the webpage with temperature value, the iot mqtt aapplication (iot_publish_2.py) available at /MiWi/Scripts/AWS/ folder has to be copied to a folder nammed iot EC2 instance virtual machine.
- Ensure that the iot mqtt certificates created are placed in iot folder and the iot_publish_2.py is updated with correct path to the certificate.
- Open EC2 instance console and execute the applicaiton using following command.
         ```
         nohup python miwi_wsn_server_4.py &
          ```
           ```
         cd iot
          ```
           ```
         nohup python iot_publish_2.py &
         ```

![](https://i.imgur.com/VXW3PDV.png)

**MiWi Setup**

For MiWi WSN Demo, program PAN-Coordinator with project file available at /MiWi/SAMR30/PAN_CORD_MOD. Program the Coordinator nodes with project file available at /MiWi/SAMR30/CORD_MOD1 and program the Sensor board with the project file available at /MiWi/SAMR30/SENSOR_MOD1.

**WSN Monitor Tool**

WSN Monitor tool is Microchip proprietary tool for 802.15.4 network monitor and contorl. In this tool, MiWi network connection with respective nodes will be displayed.
WSN Monitor toll also displayes the temperature, RSSI vlaue of the network nodes, and battery power notification.
To connect with EC2 server, EC2 instance public IP address is required. EC2 instance public IP address is available in EC2 instance page as mentioned above.
Port number for WSN monitor tool connection is `$ 8080` 
Once WSN Monitor tool connected, EC2 server will forward the packet which is received from MiWi clinet network.

![](https://i.imgur.com/Xa3a3Rn.jpg)

After the successful connection with EC2 server, WSN monitor starts receiving the MiWi network data's and displays.

![](https://i.imgur.com/cpw6Mnn.jpg)


