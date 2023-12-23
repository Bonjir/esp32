
import wifi
import time
from socket import *
import logger as log
import re
import machine
import sys
import os

SUCCESS = 0
NOTICE = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

class espremote (object):
    def __init__(self, self_ip, port):
        self.port = port
        self.ip = self_ip
        
        try:
            self.udp_addr = ('255.255.255.255', port)
            self.udp_sock = socket(AF_INET, SOCK_DGRAM)
            
            self.tcp_addr = (self_ip, port)
            self.tcp_listen_sock = socket(AF_INET, SOCK_STREAM)
            self.tcp_listen_sock.settimeout(1)
            self.tcp_listen_sock.bind(self.tcp_addr)
            self.tcp_listen_sock.listen(1)
        except Exception as exc:
            log.error(exc)
            return None
        
        self.conn = None
        self.addr = None
    
    def isconnected(self):
        return self.conn != None
    
    def recv_signal(self, description_of_this_time, expected_dat = None, timeout_no_matter = False):
        try:
            dat = self.conn.recv(1024).decode()
            if len(dat) == 0:
                log.print_only("upper comp lost connection when {}".format(description_of_this_time))
                self.conn = None
                return "", CRITICAL
            
            if expected_dat != None and dat != expected_dat:
                log.error("Response Invalid when {}. (res: {})".format(description_of_this_time, dat))
                return dat, ERROR

            return dat, SUCCESS
        
        except Exception as exc:
            if str(exc) == "[Errno 116] ETIMEDOUT" or str(exc) == "[Errno 11] EAGAIN":
                if timeout_no_matter == False:
                    log.error("No Response when {}.(exc: {})".format(description_of_this_time, exc))
                    return "", ERROR
                else:
                    return "", WARNING
            elif str(exc) == "[Errno 104] ECONNRESET" or str(exc) == "[Errno 128] ENOTCONN":
                log.print_only("upper comp lost connection when {}".format(description_of_this_time))
                self.conn = None
                return "", CRITICAL
            
            else:
                log.error("Unexpected Error when {}.(exc: {})".format(description_of_this_time, exc))
                return "", ERROR
            
        
    def send_signal(self, dat):
        try:
            self.conn.send(dat.encode())
            return True, SUCCESS
        except Exception as exc:
            log.error("Send Failed {}. {}".format(dat, exc))
            return False, CRITICAL
        
    def broadcast_and_connect(self):
        
        self.conn, self.addr = None, None
        
        message = "[HI]"
        self.udp_sock.sendto(message, self.udp_addr)
        
        # wait for accecpt tcp connection
        try:
            self.conn, self.addr = self.tcp_listen_sock.accept()
            log.info("TCP Connected to upper comp {}.".format(self.addr[0]))
            
        except Exception as exc:
            if str(exc) == "[Errno 116] ETIMEDOUT" or str(exc) == "[Errno 11] EAGAIN":
                return False
            else:
                log.error(exc)
                return False
        
        self.conn.settimeout(5.0)
        
        return True
    
    def operation_handler(self):
        
        dat, ret = self.recv_signal("ready to recv operation", None, True)
        
        if ret >= WARNING:
            return ret
        
        if dat == "[UPDATE]":
            self.send_signal("[READY]")
            return self.update()
        
        elif dat == '[REBOOT]':
            self.send_signal("[READY]")
            return self.reboot()
        
        elif dat == '[DOWNLOAD]':
            self.send_signal("[READY]")
            return self.upload()
        
        elif dat == '[GETFILELIST]':
            return self.get_file_list()
        
        elif dat == '[DELETE]':
            self.send_signal("[READY]")
            return self.delete()
        
        else:
            try:
                if dat == "":
                    log.print_only("upper comp lost connection when {}".format("received operation."))
                    self.conn = None
                    return CRITICAL
                    
                self.conn.send(dat.encode()) # echo
            except Exception as exc:
                log.error("In operation_handler(), error occurred when echo ({}). {}".format(dat, exc))
            return NOTICE
    
    def update(self):
        
        while True:
            # recv file_name
            dat, ret = self.recv_signal("recv file_name in update()")
            if ret >= WARNING:
                return ret
            
            if dat == "[END_OF_UPDATE]":
                break
            
            if not (dat.startswith('[') and dat.endswith(']')):
                log.error("Invalid Response when recv file_name in update() : {}".format(dat))
                return ERROR
            
            self.send_signal('[NAME_COPIED]')
            
            file_name = dat[1:-1]
            with open(file_name, "w+") as f:
                while True:
                    dat, ret = self.recv_signal("recv file_content in update()")
                    if ret >= WARNING:
                        return ret
                    
                    if dat.endswith("[EOF]"):
                        dat = dat[: -len("[EOF]")]
                        f.write(dat)
                        break
                    f.write(dat)
            
            self.send_signal('[CONTENT_COPIED]')
            
            log.info("Successfully update file {}.".format(file_name))
        
        self.send_signal('[FINISH]')
        return SUCCESS
    
    def reboot(self):
        self.close()
        
        log.print_only("Rebooting...")
        machine.reset()
        return SUCCESS
    
    def upload(self):
        
        while True:
            dat, ret = self.recv_signal("recv file_name in upload().")
            if ret >= WARNING:
                return ret
            
            if not (dat.startswith('[') and dat.endswith(']')):
                log.error("Invalid Response when recv file_name in upload() : {}".format(dat))
                return ERROR
            
            if dat == "[END_OF_DOWNLOAD]":
                break
            
            dat = dat[1:-1]
            file_name = dat
            
            try:
                f = open(file_name, "r+")
                arrLines = f.readlines()
                f.close()
                
                send_dat = "".join(arrLines) + "[EOF]"
                self.send_signal(send_dat)
                dat, ret = self.recv_signal("sending file_content in upload()", "[CONTENT_COPIED]")
                if ret >= WARNING:
                    return ret
                
            except Exception as exc:
                self.send_signal("[INVALID_FILE_PATH]")
                dat,ret = self.recv_signal("sending INVALID_FILE_PATH in upload()", "[COPYTHAT]")
                if ret >= WARNING:
                    return ret
                
            log.info("Successfully upload file {}.".format(file_name))
            
        self.send_signal('[FINISH]')
        return SUCCESS    
    
    def get_file_list(self):
        send_dat = str(os.listdir("./"))
        self.send_signal(send_dat)
        return SUCCESS
    
    def delete(self):
        
        dat, ret = self.recv_signal("recv file_name in delete().")
        if ret >= WARNING:
            return ret
        
        if not (dat.startswith('[') and dat.endswith(']')):
            log.error("Invalid Response when recv file_name in delete() : {}".format(dat))
            return ERROR
        dat = dat[1:-1]
        
        try:
            os.remove("./" + dat)
        
        except Exception as exc:
            log.error("Invalid file_path when recv file_name in delete() {}, {}".format(dat, exc))
            self.send_signal('[INVALID_FILE_PATH]')
            return ERROR
        
        self.send_signal('[FINISH]')
        log.info("Successfully delete file {}.".format(dat))
        return SUCCESS
    
    def close(self):
        try:
            self.udp_sock.close()
            self.conn.close()
            self.tcp_listen_sock.close()
            return SUCCESS
        except:
            return WARNING



