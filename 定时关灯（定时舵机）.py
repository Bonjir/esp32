import network
import requests
import utime
import machine
import logger as log
import ure as re
import wifi

def calibratetime():
    time_api = "http://quan.suning.com/getSysTime.do"
    
    try:
        rq = requests.get(time_api)
        info = rq.content.decode()
        rq.close()
    except Exception as exc:
        log.error("Get time info error: {}".format(exc))
        raise ValueError("Get time info error: {}".format(exc))
    
    try:
        stdtime_pattern = '"sysTime2":"(.*?)"'
        stdtime = ''
        stdtime_start = stdtime_pattern.find('(')
        
        for i in range(0, len(info)):
            info_fromi = info[i:]
            ret = re.match(stdtime_pattern, info_fromi)
            if ret != None:
                stdtime = ret.group(0)[stdtime_start : -1]
                break
            
        y = int(stdtime[0:4])
        m = int(stdtime[5:7])
        d = int(stdtime[8:10])
        h = int(stdtime[11:13])
        mn= int(stdtime[14:16])
        s = int(stdtime[17:19])
        
    except Exception as exc:
        log.error("Convert format error: {}".format(exc))
        raise ValueError("Convert format error: {}".format(exc))
    
    try:
        rtc = machine.RTC()
        rtc.datetime((y, m, d, 1, h, mn, s, 0))
    except Exception as exc:
        log.error("Set time error: {}".format(exc))
        raise ValueError("Set time error: {}".format(exc))
    
    log.print_only("Set time Success.")
    return 

def getcurrenttime():
    y, m, d, h, mn, s, _, _ = utime.localtime()
    timestr = "%04d-%02d-%02d %02d:%02d:%02d" % (y, m, d, h, mn, s)
    return timestr

from machine import Pin,PWM
import math
import time

class SERVO:
    
    def __init__(self,pin,freq=50):
        '函数的初始化'
        '参数：引脚，频率'
        self.pwm=PWM(pin,freq=freq,duty=0)
        self.freq=50 #'pwm引脚的频率，50hz正好对应20ms'
        self.Min_fx=0 #'设定最小的转动角度'
        self.Max_fx=180 #'设定最大的转动角度'
 
    def write(self,degrees=None,radians=None,sleep=0):
        '方法函数，使得舵机转过指定角度，需要用关键字的指定来设定参数。'
        '参数：角度，弧度（二者任选一），舵机sleep的时间（单位为ms）'
        if degrees==None:
            degrees=math.degrees(radians)
 
        if degrees>self.Max_fx or degrees<self.Min_fx:
            return 
        Duty=int((degrees/90+0.5)/20*1023)
        self.pwm.duty(Duty)
        time.sleep_ms(sleep)

from machine import Pin, SoftSPI,SPI
from ST7735 import TFT

spi = SoftSPI(baudrate=800000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(10))
tft = TFT(spi,6,10,7) #DC, Reset, CS

tft.initr()
tft.rgb(True)
tft.rotation(2)
tft.fill(tft.BLACK)


if __name__ == "__main__":
    
    my_servo = SERVO(Pin(8, Pin.OUT))

    color_list = [tft.BLACK, tft.RED, tft.MAROON, tft.GREEN, tft.FOREST, tft.BLUE, tft.NAVY, tft.CYAN, tft.YELLOW, tft.PURPLE, tft.WHITE, tft.GRAY]
    
    ssid = "Bonjir's ThinkBook"
    password = "bonjour866"
    ret, info = wifi.connect(ssid, password, logger_on = False)
    attempt_times = 0
    while ret == False:
        tft.textout((0, 0), "Wifi\nConnect\nTime\nOut!", tft.RED, aSize = (1.7, 1.7), auto_return = True)
        attempt_times += 1
        tft.textout((0, 90), "Attempt\nTimes:\n%d" % (attempt_times), tft.RED, aSize = (1.8, 1.8), auto_return = True, bRewrite = True)
        utime.sleep(5)
        ret, info = wifi.connect(ssid, password, logger_on = False)
    
    tft.fill(tft.BLACK)
    
    last_day_update = -1
    
    def update_local_time():
        global last_day_update
        
        try:
            calibratetime()
            y, m, d, h, mn, s, wd, yd = utime.localtime()
            info = "Last Update:\n %4d/%02d/%02d\n  %02d:%02d:%02d" % (y, m, d, h, mn, s)
            tft.textout((3, 136), info, tft.GRAY, aSize = (1, 1), auto_return = True, bRewrite = True)
            last_day_update = yd
        except Exception as exc:
            log.error("In update_local_time, catch exception as {}".format(exc))
    
    update_local_time()
    
    last_day_turn_off_light = -1 # avoid frequently shut the light in one day
    
    tft.textout((21, 49), "..", tft.WHITE, aSize = (3, 3), auto_return = True)
    
    y, m, d, h, mn, s, wd, yd = -1, -1, -1, -1, -1, -1, -1, -1
    
    while True:
        
        y, m, d, h, _mn, s, wd, yd = utime.localtime()
        
        if _mn != mn:
            mn = _mn
            
            info = "%02d" % (h)
            tft.textout((14, 20), info, tft.WHITE, aSize = (4, 4), bRewrite = True)
            info = "%02d" % (mn)
            tft.textout((14, 84), info, tft.WHITE, aSize = (4, 4), bRewrite = True)
        
        if ((h == 23 and mn == 29 and wd != 5) \
            or (h == 23 and mn == 59 and wd == 5)) and last_day_turn_off_light != yd:
            my_servo.write(degrees = 90, sleep = 1000)
            my_servo.write(degrees = 0, sleep = 1000)
            my_servo.write(degrees = 90, sleep = 1000)
            last_day_turn_off_light = yd
            
            log.info("Turn off light successfully.")
            
        if wifi.isconnected() == True and yd != last_day_update:
            update_local_time()
        
        if wifi.isconnected() == True:
            tft.textout((0, 0), "C", tft.GREEN, aSize = (1, 1), bRewrite = True)
        else:
            tft.textout((0, 0), "U", tft.RED, aSize = (1, 1), bRewrite = True)
        
#         if wifi.isconnected() == False:
#             ret, info = wifi.connect(ssid, password, logger_on = False)
#             if ret == True:
#                 udpate_local_time()
#         elif yd != last_day_update:
#             update_local_time()
        
        utime.sleep(1)
        
