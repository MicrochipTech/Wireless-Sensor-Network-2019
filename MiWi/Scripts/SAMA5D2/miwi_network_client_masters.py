import serial
import socket
import time
from threading import Thread
from threading import Lock
import sys
import os
import datetime
import struct

#change IP address based on EC2 instance IP address
SERVER_IP = '54.149.174.225'
SERVER_MIWI_NW_CLIENT_PORT = 6666

wsn_socket_flag = 0
sock_thread_flag = 0
wsn_sock = None   

wsn_socket_flag_lock = Lock()
sock_thread_flag_Lock = Lock()
wsn_sock_Lock = Lock()

def read_single_byte(port):
    single_byte_recvd = 1
    while single_byte_recvd:
        port.timeout = 0
        read_start = port.read(1)
        if (type(read_start) is str) and (read_start != ''):
            try:
                single_byte_recvd = 0
                return read_start
            except serial.SerialException as e:
                print "read_single_byte: MiWi Serial port socket closed ",e
                return
            except Exception as e:
                print "read_single_byte: read Single byte error ",e
                pass
            except KeyboardInterrupt as e:
                print "read_single_byte: User Interrupt to Termintate ",e
                os._exit(0)
        else:
            pass

def read_start_byte(port, check_byte):
    while True:
        try:
            data_read = read_single_byte(port)
            if (ord(data_read) == check_byte):
                return data_read
            else:
                pass
        except Exception as e:
            print "read_start_byte: error ",e
        except KeyboardInterrupt as e:
            print "read_start_byte: User Interrupt to Termintate ",e
            os._exit(0)

def read_end_bytes(port, miwi_recv):
    dlm_byte = 0
    stx_etx_byte = 0
    end_byte_recvd = 1
    end_byte_loop = 1    
    while end_byte_loop:
        try:
            read_byte = read_single_byte(port)
            miwi_recv.append(read_byte)
            dlm_byte = stx_etx_byte
            stx_etx_byte = ord(read_byte)
            if(dlm_byte == 0x10) and (stx_etx_byte == 0x03):
                end_byte_loop = 0
                return end_byte_recvd
            else:
                pass
        except Exception as e:
            print "read_end_bytes: error",e
        except KeyboardInterrupt as e:
            print "read_end_bytes: User Interrupt to Termintate ",e
            os._exit(0)

        

def recv_serial(port):
    miwi_recv = []    
    recv_count = 0
    start_read_seq = 0
    end_read_seq = 0
    read_byte = ''
    check_sum_byte = 0
    if port.isOpen():
        try:
            check_sum_byte = 0
            read_byte = read_start_byte(port, 0x10)
            miwi_recv.append(read_byte)
            read_byte = read_start_byte(port, 0x02)
            check_sum_byte += ord(read_byte)
            miwi_recv.append(read_byte)
            if(ord(miwi_recv[0]) == 0x10) and (ord(miwi_recv[1]) == 0x02):
                if(start_read_seq == 0) and (end_read_seq == 0):
                    start_read_seq = 1
                    if(end_read_seq == 0) and (start_read_seq == 1):
                        end_read_seq = read_end_bytes(port, miwi_recv)
                        if(start_read_seq == 1) and (end_read_seq == 1):
                            read_byte = read_single_byte(port)
                            miwi_recv.append(read_byte)
                            miwi_data = ''
                            for i in miwi_recv:
                                miwi_data+=str(i)
                            return miwi_data
        except Exception as e:
            print "recv serial exception",e
            pass
    else:
        print '[',datetime.datetime.now(),']<--', "Err - recv_serial: Com port is Closed"
        return None


def ser_recv_wsn_xmit(s, port):
    global wsn_socket_flag
    wsn_data = None
    wsn_socket_flag_temp2 = 0
    print "ser_recv_wsn_xmit: Thread Started"
    try:
        while True:
            wsn_socket_flag_lock.acquire()
            wsn_socket_flag_temp2 = wsn_socket_flag
            wsn_socket_flag_lock.release()
            try:
                if port.isOpen():
                    wsn_data = recv_serial(port)
                    try:
                        if (wsn_data != None) and (wsn_socket_flag_temp2 == 1):
                            wsn_sock_Lock.acquire()
                            if s != wsn_sock:
                                s = wsn_sock
                            wsn_sock_Lock.release()
                            s.send(wsn_data)
                            wsn_data_display = wsn_data.replace('\x10\x10','\x10')
                            print '[',datetime.datetime.now(),']-->', str(wsn_data_display[45:-3])
                    except socket.error as e:
                        print "ser_recv_wsn_xmit: MiWi NW socket error >",e
                        wsn_socket_flag_lock.acquire()
                        wsn_socket_flag = 0
                        wsn_socket_flag_lock.release()
                        pass
                    except socket.timeout as e:
                        print "ser_recv_wsn_xmit: MiWi NW socket timeout >",e
                        wsn_socket_flag_lock.acquire()
                        wsn_socket_flag = 0
                        wsn_socket_flag_lock.release()
                        pass
                    except Exception as e:
                        print "wsn_recv_ser_xmit: recv Socket Exception ",e
                        wsn_socket_flag_lock.acquire()
                        wsn_socket_flag = 0
                        wsn_socket_flag_lock.release()
                        pass
                else:
                    print "ser_recv_wsn_xmit: Com port is closed"
            except Exception as e:
                print "recv_serial",e
                pass
    except Exception as e:
        print "ser_recv_wsn_xmit", e
        pass

    

def wsn_recv_ser_xmit(s, port):
    global wsn_socket_flag 
    print "wsn_recv_ser_xmit: Thread  started"
    recv_byte = 0
    wsn_socket_flag_temp1 = 0
    try:    
        while True:
            wsn_socket_flag_lock.acquire()
            wsn_socket_flag_temp1 = wsn_socket_flag
            wsn_socket_flag_lock.release()
            try:
                wsn_sock_Lock.acquire()
                if s != wsn_sock:
                    s = wsn_sock
                wsn_sock_Lock.release()
                if wsn_socket_flag_temp1 == 1 and str(type(s)) == "<class 'socket._socketobject'>":
                    recv_byte = s.recv(1)
                    if (type(recv_byte) is str) and (recv_byte != ''):
                        try:
                            if port.isOpen():
                                port.write(recv_byte)
                        except Exception as e: 
                            print "wsn_recv_ser_xmit: port write error ",e
                            pass
            except socket.error as e:
                #print "wsn_recv_ser_xmit: recv Socket error ",e
                #wsn_socket_flag_lock.acquire()
                #wsn_socket_flag = 0
                #wsn_socket_flag_lock.release()
                pass
            except socket.timeout as e:
                #print "wsn_recv_ser_xmit: recv Socket timeout ",e
                #wsn_socket_flag_lock.acquire()
                #wsn_socket_flag = 0
                #wsn_socket_flag_lock.release()
                pass
            except Exception as e:
                print "wsn_recv_ser_xmit: recv Socket Exception ",e
                wsn_socket_flag_lock.acquire()
                wsn_socket_flag = 0
                wsn_socket_flag_lock.release()
                pass
    except Exception as e:
        print "wsn_recv_ser_xmit",e
        pass

def wsn_socket(port):
    global wsn_socket_flag
    global sock_thread_flag
    global wsn_sock
    wsn_socket_flag_temp = 0
    wsn_sock_temp = ''
    while True:
        wsn_socket_flag_lock.acquire()
        wsn_socket_flag = 0
        wsn_socket_flag_lock.release()
        wsn_sock_Lock.acquire()
        wsn_sock_temp = wsn_sock
        wsn_sock_Lock.release()
        try:
            if str(type(wsn_sock_temp)) == "<class 'socket._socketobject'>":
                wsn_sock_Lock.acquire()
                try:
                    wsn_sock.close()
                except:
                    pass
                wsn_sock_Lock.release()
            wsn_sock_Lock.acquire()
            wsn_sock = None
            wsn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            wsn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            wsn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,struct.pack('ii', 1, 0))
            wsn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, struct.pack('ll', 30, 0))
            #wsn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            #wsn_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
            #wsn_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
            #wsn_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
            wsn_sock.settimeout(30)
            print '[',datetime.datetime.now(),'] ', 'Connecting to Server'
            wsn_sock.connect((SERVER_IP,SERVER_MIWI_NW_CLIENT_PORT))
            wsn_sock_Lock.release()
            time.sleep(1)
            print '[',datetime.datetime.now(),'] ', 'Connected to Server'
            time.sleep(2)
            sock_thread_flag_Lock.acquire()
            sock_thread_flag = 1
            sock_thread_flag_Lock.release()
            wsn_socket_flag_lock.acquire()
            wsn_socket_flag = 1
            wsn_socket_flag_temp = wsn_socket_flag
            wsn_socket_flag_lock.release()
            sock_thread_flag_Lock.acquire()
            print "wsn_socket:sock_thread_flag=",sock_thread_flag
            sock_thread_flag_Lock.release()
            while wsn_socket_flag_temp == 1:
                time.sleep(10)
                wsn_socket_flag_lock.acquire()
                wsn_socket_flag_temp = wsn_socket_flag
                wsn_socket_flag_lock.release()
            print '[',datetime.datetime.now(),'] ',"Server Socket Connection loss"
            wsn_sock_Lock.acquire()
            try:
                wsn_sock.close()
                time.sleep(2)
            except:
                pass
            wsn_sock_Lock.release()
        except socket.error as e:
            print "wsn_socket: Socket failed to connect ",e
            if wsn_sock_Lock.locked():
                wsn_sock_Lock.release()
            wsn_sock_Lock.acquire()
            try:
                wsn_sock.close()
                time.sleep(2)
            except:
                pass
            pass
            wsn_sock_Lock.release()
        finally:
            try:
                if wsn_socket_flag_lock.locked():
                    wsn_socket_flag_lock.release()
            except:
                pass
            try:
                if wsn_sock_Lock.locked():
                    wsn_sock_Lock.release()
            except:
                pass
            time.sleep(15)

def Main():
    global sock_thread_flag
    global wsn_sock
    wsn_sock = ''
    try:
        port = serial.Serial("/dev/ttyACM0", baudrate=38400, timeout=0, xonxoff=False, rtscts=True, dsrdtr=False)
        print "Serial port Opened %d",port
        sock_thread = Thread(target=wsn_socket, args=(port,))
        sock_thread.start()
        print "Main: sock_thread.started"
        thread_flag = 0
        while thread_flag == 0:
            sock_thread_flag_Lock.acquire()
            sock_thread_flag_temp = sock_thread_flag
            sock_thread_flag_Lock.release()
            if sock_thread_flag_temp == 1:
                print "Creating Threads\n"
                print "wsn_sock: ",wsn_sock
                recv_thread = Thread(target=ser_recv_wsn_xmit, args=(wsn_sock, port))
                xmit_thread = Thread(target=wsn_recv_ser_xmit, args=(wsn_sock, port))
                recv_thread.start()
                xmit_thread.start()
                print "Created Threads\n"
                thread_flag = 1
            print "waiting in main\n", sock_thread_flag_temp
            time.sleep(15)
        sock_thread.join()
    except Exception as e:
        print "Main: exception", e
       

if __name__ == '__main__':
    Main()
