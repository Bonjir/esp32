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
        
my_servo = SERVO(Pin(8, Pin.OUT))

while True:
    my_servo.write(degrees = 0, sleep = 1000)
    my_servo.write(degrees = 45, sleep = 1000)
    my_servo.write(degrees = 90, sleep = 1000)
    my_servo.write(degrees = 135, sleep = 1000)
    my_servo.write(degrees = 180, sleep = 3000)
