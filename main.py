import _thread

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect("Redmi Note 10 Pro", '97587890')
        while not sta_if.isconnected():
            pass
    print('Connected! Network config:', sta_if.ifconfig())
    
print("Connecting to your wifi...")
do_connect()


from random import randint
from microdot import Microdot, send_file
from microdot_websocket import with_websocket
from time import sleep



#system part

import dht
from machine import Timer, Pin, ADC, SoftI2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

#Temp humid  pin 18
#gaz pin 32
# buzzer pin 2

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)     #initializing the I2C method for ESP32
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

sensorDht = dht.DHT11(Pin(4, Pin.OUT))
sensorGaz = ADC(Pin(32, Pin.IN))

dcMotor = Pin(18, Pin.OUT)
buzzer = Pin(19, Pin.OUT)











def fun():
    try:
        temp = sensorDht.measure() 
        global temprature
        temprature = sensorDht.temperature()
        global humidity
        humidity = sensorDht.humidity()
    except:
        temprature = 0
        humidity = 0
        print('Faild to Read')
    
    lcd.move_to(0,0)
    lcd.putstr('Temperature: ' + str(temprature))
    lcd.move_to(0,1)
    lcd.putstr('Humidity: ' + str(humidity))
    
    
    if temprature > 20:
        dcMotor.value(1)
    else:
        dcMotor.value(0)
        print(dcMotor.value())
    
    if sensorGaz.read() > 2048:
        
        buzzer.value(1)
        print(buzzer.value())
    else:
        buzzer.value(0)
        print(buzzer.value())
    
    print(sensorGaz.read()) 
    










app = Microdot()


@app.route('/')
def index(request):
    return send_file('index.html')



@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path)


@app.route('/echo')
@with_websocket
def echo(request, ws):
    while True:
        ws.send(str(temprature) + ', ' + str(humidity))
        sleep(0.5)



@app.route('/shutdown')
def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


_thread.start_new_thread(fun, ())
app.run()

