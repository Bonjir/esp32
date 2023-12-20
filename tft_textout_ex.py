from machine import Pin, SoftSPI,SPI
from ST7735 import TFT

spi = SoftSPI(baudrate=800000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(10))
tft = TFT(spi,6,10,7) #DC, Reset, CS

tft.initr()
tft.rgb(True)
tft.rotation(1)
tft.fill(tft.BLACK)

if __name__ == '__main__':
    
    color_list = [tft.BLACK, tft.RED, tft.MAROON, tft.GREEN, tft.FOREST, tft.BLUE, tft.NAVY, tft.CYAN, tft.YELLOW, tft.PURPLE, tft.WHITE, tft.GRAY]
    
    string = "abc \n 1234567\n1234567890abcdefghijklmno"
    tft.textout((10, 0), string, tft.BLUE, aSize = (2, 2))
    
    string = "A lazy fox jumps."
    tft.setfontsize((2, 1))
    tft.textout((20, 5), string, tft.GREEN, aSize = (2, 1))