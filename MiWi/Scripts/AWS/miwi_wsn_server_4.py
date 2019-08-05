import socket
import time
import threading
import datetime
from threading import Thread
from threading import Lock
import os
import sys
import struct

wsn_sock_xmit_list = []
miwi_sock_recv_list = []
miwi_wsn_packet = []
wsn_client_count = 0

SERVER_IP = '0.0.0.0'
SERVER_WSN_CLIENT_PORT = 8080
SERVER_MIWI_NW_CLIENT_PORT = 6666

tLock = Lock()
wsn_sock_xmit_listLock = Lock()
miwi_sock_recv_listLock = Lock()
wsn_client_countLock = Lock()

def wsn_client_socket():
    global wsn_client_count
    wsn_client_count_copy1 = 0
    try:
        print "Creating WSN socket"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((SERVER_IP, SERVER_WSN_CLIENT_PORT))
        s.listen(32)
        wsn_client_countLock.acquire()
        wsn_client_count = 0
        wsn_client_count_copy1 = wsn_client_count
        wsn_client_countLock.release()
        while True:
            print 'waiting for connection from WSN Tool ',[wsn_client_count_copy1]
            sys.stdout.flush()
            c, addr = s.accept()
            c.settimeout(3600)
            wsn_sock_xmit_listLock.acquire()
            wsn_sock_xmit_list.append(c)
            wsn_sock_xmit_listLock.release()
            wsn_client_countLock.acquire()
            wsn_client_count+=1
            wsn_client_count_copy1 = wsn_client_count
            wsn_client_countLock.release()
            print "Connection form: ",str(addr),c
            sys.stdout.flush()
    except socket.error as e:
        print "wsn_client_socket: socket error> ",e
        sys.stdout.flush()
        if(wsn_client_count_copy1 != 0):
            try:
                c.close()
            except:
                pass
            if wsn_sock_xmit_listLock.locked():
                wsn_sock_xmit_listLock.release()
            wsn_sock_xmit_listLock.acquire()
            try:
                wsn_sock_xmit_list.remove(c)
            except:
                pass
            wsn_sock_xmit_listLock.release()
            if wsn_client_countLock.locked():
                wsn_client_countLock.release()
            wsn_client_countLock.acquire()
            try:                    
                wsn_client_count-=1
                wsn_client_count_copy1 = wsn_client_count
            except:
                pass
            wsn_client_countLock.release()
        pass
    except Exception as e:
        print "wsn_client_socket: accept error> ",e
        sys.stdout.flush()
        if(wsn_client_count_copy1 != 0):
            try:
                c.close()
            except:
                pass
            if wsn_sock_xmit_listLock.locked():
                wsn_sock_xmit_listLock.release()
            wsn_sock_xmit_listLock.acquire()
            try:
                wsn_sock_xmit_list.remove(c)
            except:
                pass
            wsn_sock_xmit_listLock.release()
            if wsn_client_countLock.locked():
                wsn_client_countLock.release()
            wsn_client_countLock.acquire()
            wsn_client_count-=1
            wsn_client_count_copy1 = wsn_client_count
            wsn_client_countLock.release()
        pass

def wsn_xmit():
    global wsn_client_count
    wsn_data = ''
    while True:
        try:
            wsn_sock_xmit_listLock.acquire()
            try:
                wsn_sock_xmit_list_copy = wsn_sock_xmit_list
            except:
                wsn_sock_xmit_list_copy = []
                pass
            wsn_sock_xmit_listLock.release()
            wsn_data = ''
            if len(wsn_sock_xmit_list_copy) != 0:
                tLock.acquire()
                try:
                    if len(miwi_wsn_packet) !=0:
                        while len(miwi_wsn_packet):
                            wsn_data += miwi_wsn_packet.pop()
                    else:
                        wsn_data = ''
                except:
                    pass
                tLock.release()
                if len(wsn_data) != 0:
                    for j in wsn_sock_xmit_list_copy:
                        try:
                            j.send(wsn_data)
                        except socket.error as e:
                            print "wsn_xmit: send wsn socket error> ",e
                            sys.stdout.flush()
                            if((len(wsn_sock_xmit_list_copy)) != 0):
                                if wsn_client_countLock.locked():
                                    wsn_client_countLock.release()
                                wsn_client_countLock.acquire()
                                wsn_client_count-=1
                                wsn_client_countLock.release()
                                if wsn_sock_xmit_listLock.locked():
                                    wsn_sock_xmit_listLock.release()
                                wsn_sock_xmit_listLock.acquire()
                                try:
                                    j.close()
                                    wsn_sock_xmit_list.remove(j)
                                    wsn_sock_xmit_list_copy = wsn_sock_xmit_list
                                except:
                                    pass
                                wsn_sock_xmit_listLock.release()
                            pass
                        except Exception as e:
                            print "wsn_xmit: packet send error ",e
                            sys.stdout.flush()
                            if((len(wsn_sock_xmit_list_copy)) != 0):
                                if wsn_client_countLock.locked():
                                    wsn_client_countLock.release()
                                wsn_client_countLock.acquire()
                                wsn_client_count-=1
                                wsn_client_countLock.release()
                                if wsn_sock_xmit_listLock.locked():
                                    wsn_sock_xmit_listLock.release()
                                wsn_sock_xmit_listLock.acquire()
                                try:
                                    j.close()
                                    wsn_sock_xmit_list.remove(j)
                                    wsn_sock_xmit_list_copy = wsn_sock_xmit_list
                                except:
                                    pass
                                wsn_sock_xmit_listLock.release()
                    wsn_data_display = wsn_data.replace('\x10\x10','\x10')
                    print '[',datetime.datetime.now(),']-->', str(wsn_data_display[45:45+ord(wsn_data_display[44])])
                    sys.stdout.flush()
        except Exception as e:
            print "wsn_xmit: packet send error> ",e
            sys.stdout.flush()
            pass

def wsn_recv():
    global wsn_client_count
    recv_byte = ''
    while True:
        try:
            wsn_sock_xmit_listLock.acquire()
            try:
                wsn_sock_xmit_list_copy2 = wsn_sock_xmit_list
            except:
                wsn_sock_xmit_list_copy2 = []
                pass
            wsn_sock_xmit_listLock.release()
            if((len(wsn_sock_xmit_list_copy2)) != 0):
                for i in wsn_sock_xmit_list_copy2:
                    try:
                        recv_byte = i.recv(1)
                    except socket.timeout as timeout:
                        pass
                    except socket.error as e:
                        print "wsn_recv: recv socket closed ",e
                        sys.stdout.flush()
                        if wsn_client_countLock.locked():
                            wsn_client_countLock.release()
                        wsn_client_countLock.acquire()
                        wsn_client_count_copy2 = wsn_client_count
                        wsn_client_countLock.release()
                        if(wsn_client_count_copy2 != 0):
                            if wsn_client_countLock.locked():
                                wsn_client_countLock.release()
                            wsn_client_countLock.acquire()
                            wsn_client_count-=1
                            wsn_client_count_copy2 = wsn_client_count
                            wsn_client_countLock.release()
                            i.close()
                            if wsn_sock_xmit_listLock.locked():
                                wsn_sock_xmit_listLock.release()
                            wsn_sock_xmit_listLock.acquire()
                            try:
                                wsn_sock_xmit_list.remove(i)
                                wsn_sock_xmit_list_copy2 = wsn_sock_xmit_list
                            except:
                                pass
                            wsn_sock_xmit_listLock.release()
                        pass
                    miwi_sock_recv_listLock.acquire()
                    try:
                        miwi_sock_recv_list_copy = miwi_sock_recv_list
                    except Exception as e:
                        miwi_sock_recv_list_copy = []
                        print "wsn_recv: packet recv error> ",e
                        sys.stdout.flush()
                        pass
                    miwi_sock_recv_listLock.release()
                    if((recv_byte != 0) and ((len(miwi_sock_recv_list_copy)) != 0)):
                        for j in miwi_sock_recv_list_copy:
                            try:
                                j.send(recv_byte)
                            except:
                                pass
        except Exception as e:
            print "wsn_recv: packet recv error> ",e
            sys.stdout.flush()
            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            pass

def read_single_byte(conn):
    single_byte_recvd = False
    empty_count = 0
    while single_byte_recvd == False:
        try:
            read_byte = conn.recv(1)
        except socket.error as e:
            print "read_single_byte: socket erro -> MiWi NW socket closed >",e
            sys.stdout.flush()
            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            miwi_sock_recv_listLock.acquire()
            try:
                conn.close()
                miwi_sock_recv_list.remove(conn)
            except:
                pass
            miwi_sock_recv_listLock.release()
            pass
            return -1
        except socket.timeout as timeout:
            print "read_single_byte: socket erro -> MiWi NW socket timeout >",e
            sys.stdout.flush()
            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            miwi_sock_recv_listLock.acquire()
            try:
                conn.close()
                miwi_sock_recv_list.remove(conn)
            except:
                pass
            miwi_sock_recv_listLock.release()
            pass
            return -1
        if (type(read_byte) is str) and (read_byte != ''):
            single_byte_recvd = True
            return read_byte
        else:
            empty_count+=1
            if(empty_count >= 100):
                print "read_single_byte: Null packet received"
                sys.stdout.flush()
                if miwi_sock_recv_listLock.locked():
                    miwi_sock_recv_listLock.release()
                miwi_sock_recv_listLock.acquire()
                try:
                    conn.close()
                    miwi_sock_recv_list.remove(conn)
                except:
                    pass
                miwi_sock_recv_listLock.release()
                pass
                return -1
                


def read_miwi_data(conn):
    data_recvd_flag = False
    start_byte_recvd = False
    miwi_read_data = ''
    while True:
        data_read = read_single_byte(conn)
        if data_read == -1:
            return -1
        elif data_read == '\x10':
            data_read = read_single_byte(conn)
            if data_read == -1:
                return -1
            if data_read == '\x02':
                start_byte_recvd = True
        if start_byte_recvd == True:
            start_byte_recvd = False
            miwi_read_data = '\x10\x02'
            end_byte_loop = True
            dlm_byte = ''
            stx_etx_byte = ''
            while end_byte_loop:
                read_byte = read_single_byte(conn)
                if(read_byte == -1):
                    return -1
                miwi_read_data += read_byte
                dlm_byte = stx_etx_byte
                stx_etx_byte = read_byte
                if(dlm_byte == '\x10') and (stx_etx_byte == '\x03'):
                    end_byte_loop = False
            read_byte = read_single_byte(conn)
            if(read_byte == -1):
                return -1
            miwi_read_data += read_byte
            return miwi_read_data
            

def miwi_packet_recv():
    miwi_data = ''
    miwi_data_flag = False
    while True:
        try:
            miwi_sock_recv_listLock.acquire()
            try:
                miwi_sock_recv_list_len = len(miwi_sock_recv_list)
                miwi_sock_recv_list_temp = miwi_sock_recv_list
            except:
                pass
            miwi_sock_recv_listLock.release()
        except:
            pass
        if miwi_sock_recv_list_len:
            for conn in miwi_sock_recv_list_temp:
                try:
                    miwi_data = read_miwi_data(conn)
                    if miwi_data != -1:
                        miwi_data_flag = True
                except Exception as e:
                    print "miwi_packet_recv: socket connection closed>",e
                    try:
                        miwi_sock_recv_listLock.acquire()
                        miwi_sock_recv_list.remove(conn)
                        miwi_sock_recv_listLock.release()
                        conn.close()
                    except:
                        pass
                    pass
                if miwi_data_flag == True:
                    try:
                        tLock.acquire()
                        try:
                            if (len(miwi_wsn_packet) >= 1000):
                                temp = miwi_wsn_packet.pop(0)
                            miwi_wsn_packet.append(miwi_data)
                        except Exception as e:
                            print "miwi_packet_recv: len_wsn_sock_xmit_list>",e
                            sys.stdout.flush()
                            pass
                        tLock.release()
                        miwi_data_flag = False
                    except:
                        pass


def miwi_nw_client_socket():
    try:
        print "Creating MiWI bridge socket"
        sys.stdout.flush()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,struct.pack('ii', 1, 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('ll', 30, 0))
        s.bind((SERVER_IP, SERVER_MIWI_NW_CLIENT_PORT))
        s.listen(32)
        s.settimeout(3600)
    except Exception as e:
        print "miwi_nw_client_socket: MiWi NW socket creation error > ",e
        sys.stdout.flush()
        try:
            s.close()
        except:
            pass
        sys.exit(1)
    while True:
        try:
            print '[',datetime.datetime.now(),']-->','waiting for connection from MiWi BRidge'
            sys.stdout.flush()
            c, addr = s.accept()
            print '[',datetime.datetime.now(),']-->',"MiWi Connection form: ",str(addr),c
            sys.stdout.flush()
            c.settimeout(60)
            if miwi_sock_recv_listLock.locked():
                print "miwi_nw_client_socket: miwi_sock_recv_listLock is locked"
                sys.stdout.flush()
                time.sleep(5)
                if miwi_sock_recv_listLock.locked():
                    try:
                        miwi_sock_recv_listLock.release()
                        print "miwi_nw_client_socket: miwi_sock_recv_listLock released!!"
                        sys.stdout.flush()
                    except:
                        pass
            miwi_sock_recv_listLock.acquire()
            miwi_sock_recv_list.append(c)
            for i in miwi_sock_recv_list:
                print "Miwi_sock_list - ",i
                sys.stdout.flush()
            miwi_sock_recv_listLock.release()
        except socket.error as e:
            print "miwi_nw_client_socket: NW socket closed> ",e
            sys.stdout.flush()
            time.sleep(10)

            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            miwi_sock_recv_listLock.acquire()
            try:
                c.close()
                miwi_sock_recv_list.remove(c)
            except:
                pass
            miwi_sock_recv_listLock.release()
            pass
        except socket.timeout as timeout:
            print "miwi_nw_client_socket: NW socket timeout> ",e
            sys.stdout.flush()
            time.sleep(10)

            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            miwi_sock_recv_listLock.acquire()
            try:
                c.close()
                miwi_sock_recv_list.remove(c)
            except:
                pass
            miwi_sock_recv_listLock.release()
            pass
        except Exception as e:
            print "miwi_nw_client_socket: MiWi NW socket exception > ",e
            sys.stdout.flush()
            time.sleep(10)

            if miwi_sock_recv_listLock.locked():
                miwi_sock_recv_listLock.release()
            miwi_sock_recv_listLock.acquire()
            try:
                c.close()
                miwi_sock_recv_list.remove(c)
            except:
                pass
            miwi_sock_recv_listLock.release()
            pass

def Main():
        miwi_client_thread = 0
        wsn_client_thread = 0
        wsn_xmit_thread = 0
        wsn_recv_thread = 0
        miwi_packet_recv_thread = 0
        try:
                miwi_client_thread = Thread(target=miwi_nw_client_socket, args=())
                wsn_client_thread = Thread(target=wsn_client_socket, args=())
                wsn_xmit_thread = Thread(target=wsn_xmit, args=())
                wsn_recv_thread = Thread(target=wsn_recv, args=())
                miwi_packet_recv_thread = Thread(target=miwi_packet_recv, args=())

                miwi_client_thread.start()
                time.sleep(1)
                wsn_client_thread.start()
                time.sleep(1)
                wsn_xmit_thread.start()
                time.sleep(1)
                wsn_recv_thread.start()
                time.sleep(5)
                miwi_packet_recv_thread.start()

                miwi_client_thread.join()
                wsn_client_thread.join()
                wsn_xmit_thread.join()
                wsn_recv_thread.join()
                #miwi_packet_recv_thread.join()
                while True:
                        time.sleep(10)
        except Exception as e:
                print "Main: thread error>",e
                sys.stdout.flush()
                miwi_client_thread.close()
                wsn_client_thread.close()
                wsn_xmit_thread.close()
                wsn_recv_thread.close()
                #miwi_packet_recv_thread.close()
                os._exit()

        except KeyboardInterrupt as e:
                print "Main: User Interrupt to Termintate ",e
                sys.stdout.flush()
                miwi_client_thread.close()
                wsn_client_thread.close()
                wsn_xmit_thread.close()
                wsn_recv_thread.close()
                os._exit(0)
if __name__ == '__main__':
        Main()
