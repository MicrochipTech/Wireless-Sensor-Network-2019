import socket
import sys
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from threading import Thread
import json

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

#change ip address with the one created during EC2 instance on Amazon Cloud
ip = '54.149.174.225'
port = 8080

miwi_data = ''
miwi_topic = "/Microchip/WSN_Demo/MiWi"
json_data_dict = {'nodeID': "Node1", 'Battery': "3.30V", 'Temperature': 77.00, 'RSSI': -100}

iot_mqtt_connect_flag = False
miwiMQTTClient = ''


def int_2_comp_str(val):
    try:
        if val & 0x80:
            comp_val = ((~val) & 0x7F) + 1
            return_value = (-1 * comp_val)
        else:
            return_value = (val)
    except Exception as e:
        print "int_2_comp_str",e
        return_value = '-100'
        pass
    finally:
        return return_value
    
def miwi_iot_mqtt(iot_data):
    global miwiMQTTClient
    global iot_mqtt_connect_flag
    device_name = ''
    device_id = ''
    name_index = 0
    temperature = 77
    battery = 25.00
    rssi_str = '0'
    json_data = ''
    json_data_flag = False
    if iot_data[0:2] == '\x10\x02' and iot_data[-3:-1] == '\x10\x03':
        iot_data = iot_data.replace('\x10\x10','\x10')
        for s_id in USMastersNodeLocation:
            wsn_name_flag = False
            try:
                name_index = iot_data.find(USMastersNodeLocation[s_id])
                if name_index > 44 and ord(iot_data[name_index-2]) == 32:
                    device_name = iot_data[name_index:-3]
                    #device_name = iot_data[name_index:-10] #remove short address
                    device_id = s_id
                    name_len = ord(iot_data[name_index-1])
                    wsn_name_flag = True
                    if device_name == USMastersNodeLocation[device_id]:
                        break
            except Exception as e:
                wsn_name_flag = False
                print "miwi_iot_mqtt: name id error1> ",e 
                pass
        if wsn_name_flag == False:
            try:
                if iot_data.find("Router")==-1 and iot_data.find("MiWi Bridge")==-1:
                    #iot_data[43] - name.type
                    print "Unknow Device data:",iot_data[45:-3]                    
                    sys.stdout.flush()
                else:
                    #print "Received Coordinator data:",iot_data[45:-3]
                    sys.stdout.flush()
            except Exception as e:
                print "miwi_iot_mqtt: name id error2> ",e 
                pass
        else:
            try:
                sensor_check = iot_data[29:31]
            except Exception as e:
                 print "miwi_iot_mqtt: sensor_check error> ",e 
                 pass
            if sensor_check == '\x01\x0c':
               try:
                    #print "Sensor Node:",iot_data[45:-3]
                    #light is iot_data[39:43]
                    temp_str = iot_data[35:39]
                    temperature = ord(temp_str[0])+(ord(temp_str[1])*256)+(ord(temp_str[2])*65536)+(ord(temp_str[2])*16777216)
                    #temperature = (temperature * 1.8) + 32
                    if (temperature > 200) or (temperature < 32):
                        temperature = 77
               except Exception as e:
                    print "miwi_iot_mqtt: temperature conversion error> ",e 
                    pass
               try:
                    battery_str = iot_data[31:35]
                    battery = float(ord(battery_str[0])+(ord(battery_str[1])*256)+(ord(battery_str[2])*65536)+(ord(battery_str[2])*16777216))/1000
                    if (battery > 100) or (battery < 0):
                        battery = 25.00
               except Exception as e:
                    print "miwi_iot_mqtt: temperature conversion error> ",e 
                    pass
            else:
                print "miwi_iot_mqtt: sensor_check failed"
                print "Sensor val",hex(ord(sensor_check[0])),hex(ord(sensor_check[1]))
            try:
                rssi_str = int_2_comp_str(ord(iot_data[28]))
            except Exception as e:
                print "miwi_iot_mqtt: rssi error> ",e 
                rssi_str = '100'
                pass
            try:
                json_data_dict['nodeID'] = device_id
                json_data_dict['Temperature'] = temperature
                json_data_dict['RSSI'] = rssi_str
                json_data = json.dumps(json_data_dict)
                json_data_flag = True
            except Exception as e:
                print "miwi_iot_mqtt: json_data_dict error > ",e 
                rssi_str = '100'
                pass
            if json_data_flag == True:
                json_data_flag = False
                if iot_mqtt_connect_flag == True:
                    try:
                        print device_name,'-->',json_data
                        miwiMQTTClient.publish(miwi_topic, json_data, 1)
                    except Exception as e:
                        print "miwi_iot_mqtt: mqtt publish> ",e
                        pass

def wsn_client_socket():
    server_connect_flag = False
    global miwiMQTTClient
    while True:
        if server_connect_flag == False:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Connect the socket to the port where the server is listening.
                server_address = (ip, port)
                print 'Connecting to %s port %s...' % server_address
                sock.connect(server_address)
                server_connect_flag = True
                print 'Connected to %s port %s...' % server_address
            except Exception as e:
                print "wsn client scoket connectoin error ",e
                server_connect_flag = False
                pass
        if server_connect_flag == True:
            start_index = -1
            data = ''
            while True:
                miwi_data = ''
                #data = ''
                miwi_data_flag = False
                try:
                    data += sock.recv(100)
                except Exception as e:
                    server_connect_flag = True
                    print "wsn client socket connection closed>",e
                    try:
                        sock.close()
                    except:
                        pass
                    break
                if start_index == -1:
                    start_index = data.find('\x10\x02')
                if start_index != -1:
                    end_index = data.find('\x10\x03')
                    if end_index != -1:
                        miwi_data = data[start_index:end_index+3]
                        data = data[end_index+3:]
                        miwi_data_flag = True
                    else:
                        data=data[start_index:]
                if miwi_data_flag == True:
                    miwi_iot_mqtt(miwi_data)
                    miwi_data_flag = False
    
def aws_iot_connect():
    global iot_mqtt_connect_flag
    global miwiMQTTClient
    iot_mqtt_connect_flag = False
    while not(iot_mqtt_connect_flag):
        try:
            print "Connecting to AWS MQTT client"
            # For certificate based connection
            miwiMQTTClient = AWSIoTMQTTClient("MiWiBridgeClientID")
            # For TLS mutual authentication with TLS ALPN extension
            miwiMQTTClient.configureEndpoint("a3adakhi3icyv9.iot.us-west-2.amazonaws.com", 443)
            miwiMQTTClient.configureCredentials("AmazonRootCA1.pem", "9bea20e761-private.pem.key", "9bea20e761-certificate.pem")
            miwiMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            miwiMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            miwiMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            miwiMQTTClient.configureMQTTOperationTimeout(15)  # 5 sec
            miwiMQTTClient.connect()
            print "Connected to AWS MQTT client"
            iot_mqtt_connect_flag = True
            sys.stdout.flush()
        except Exception as e:
            print "miwi_iot_mqtt: mqtt connect error> ",e
            sys.stdout.flush()
            pass

        

def Main():
    try:
        wsn_client_thread = 0
        aws_connect_thread = 0
        wsn_client_thread = Thread(target=wsn_client_socket, args=())
        aws_connect_thread = Thread(target=aws_iot_connect, args=())
        time.sleep(1)
        wsn_client_thread.start()
        aws_connect_thread.start()
        wsn_client_thread.join()
        aws_connect_thread.join()
    except Exception as e:
        print "Main: thread error>",e
        wsn_client_thread.close()

            
if __name__ == '__main__':
        Main()
        
        

