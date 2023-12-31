import network
import requests
import utime
import logger as log

CONNECT_TIMEOUT = 3000 # ms
wifi = None
ipaddr = ""

def connect(ssid, password, logger_on = True):
    
    global CONNECT_TIMEOUT
    global wifi
    global ipaddr
    
    wifi = network.WLAN(network.STA_IF)

    if wifi.isconnected() == True:
        wifi.disconnect()
        
    wifi.active(False)
    wifi.active(True)
    wifi.connect(ssid, password)

    connect_time = utime.ticks_ms()
    while wifi.isconnected() == False:
        if utime.ticks_ms() - connect_time >= CONNECT_TIMEOUT:
            if logger_on == True:
                log.error("Connect time out!")
            else:
                log.print_only("Connect time out!")
            return False, "Wifi Connect Timeout!"
        else:
            pass
    
    ipaddr = wifi.ifconfig()[0]
    if logger_on == True:
        log.info("Connection successful, IP Address: {}".format(ipaddr))
    else:
        log.print_only("Connection successful, IP Address: {}".format(ipaddr))
    return True, ipaddr

def isconnected():
    return wifi.isconnected()

def disconnect(self):
    global wifi
    wifi.disconnect()

# def _ping_baidu():
#     rq = requests.get("http://www.baidu.com")
#     if rq.status_code != 200 or "Example Domain" not in rq.text:
#         log.info("Unconnected to the Internet!")
#         rq.close()
#         return False
#     else:
#         log.info("Connected to the Internet!")
#         rq.close()
#         return True

def ping():
    rq = requests.get("http://www.example.com")
    if rq.status_code != 200 or "Example Domain" not in rq.text:
        log.info("Unconnected to the Internet!")
        rq.close()
        return False
    else:
        log.info("Connected to the Internet!")
        rq.close()
        return True
    
