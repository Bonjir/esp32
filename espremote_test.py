
import espremote
import wifi
import sys

SSID = "Bonjir's ThinkBook"
PASSWORD = "bonjour866"
PORT = 8668

if __name__ == "__main__":
    
    ret, ip = wifi.connect(SSID, PASSWORD, logger_on = False)
    
    if not ret:
        print("network fucked off")
        sys.exit()
    
    uc = espremote.espremote(ip, PORT)
    if uc == None:
        print("init fucked off")
        sys.exit()
        
    print("waiting for tcp connect...")
    while True:
        ret = uc.broadcast_and_connect()
        if ret:
            break
    
    while True:
        ret = uc.operation_handler()
        if not uc.isconnected():
            break
    
    pass

