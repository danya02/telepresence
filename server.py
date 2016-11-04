#!/usr/bin/python3
import gpiozero
# import magic.video.transmitter as videoout
# import magic.video.reciever as videoin
import paho.mqtt.client as mqtt
import os
import time
SERVER = "127.0.0.1"
TOPIC = "drone1"
global motorstat
motorstat = "STOP"
global base


class ArduinoMotor:
	def __init__(self):
		self.dirleft = gpiozero.LED(17)
		self.dirright = gpiozero.LED(22)
		self.motorleft = gpiozero.LED(18)
		self.motorright = gpiozero.LED(23)

	def __exit__(self):
		self.dirright.close()
		self.dirleft.close()
		self.motorright.close()
		self.motorleft.close()

	def forward(self):
		self.dirright.off()
		self.dirleft.off()
		self.motorright.on()
		self.motorleft.on()

	def back(self):
		self.dirright.on()
		self.dirleft.on()
		self.motorright.on()
		self.motorleft.on()

	def left(self):
		self.dirright.off()
		self.dirleft.on()
		self.motorright.on()
		self.motorleft.on()

	def right(self):
		self.dirright.on()
		self.dirleft.off()
		self.motorright.on()
		self.motorleft.on()

	def stop(self):
		self.motorright.off()
		self.motorleft.off()

base = ArduinoMotor()
global display_relay
display_relay = gpiozero.LED(3)
kill_switch = gpiozero.LED(4, initial_value=True)
c = mqtt.Client()
c.will_set(TOPIC, "DEAD", qos=2)
c.connect(SERVER)
c.subscribe(TOPIC, qos=1)
c.publish("ALIVE", TOPIC)


def on_message(client, userdata, m):
    global motorstat
    global videoinstat
    global display_relay
    global base
    m = m.payload
    try:
        if b"ACK" in m:
            client.publish(TOPIC, str(m.split(b":")[0][2:-1])+":"+"RACK")
            raise IndexError
        elif b"MOVE" in m:
            if b"FORWARD" in m:
                base.forward()
                motorstat = "FORWARD"
            elif b"BACK" in m:
                base.back()
                motorstat = "BACK"
            elif b"LEFT" in m:
                base.left()
                motorstat = "LEFT"
            elif b"RIGHT" in m:
                base.right()
                motorstat = "RIGHT"
        elif b"STOP" in m:
            base.stop()
            motorstat = "STOP"
        elif b"MOTORSTAT" in m:
            client.publish(TOPIC, str(m.split(b":")[0])[2:-1]+":"+motorstat)
            raise IndexError
        elif b"DISPLAY" in m:
            if b"ON" in m:
                display_relay.on()
            elif b"OFF" in m:
                display_relay.on()
            elif b"STATUS" in m:
                client.publish(TOPIC, str(m.split(b":")[0])[2:-1]+("ON" if display_relay.is_lit else "OFF"))
                raise IndexError
        elif b"REBOOT" in m:
            os.popen("shutdown -r now")
            time.sleep(10)
            raise IOError
        elif b"POWERCYCLE" in m:
            kill_switch.off()
            time.sleep(5)
            raise IOError
        elif b"VIDEOIN" in m:
            if b"ON" in m:
                # videoin.start()
                videoinstat = True
            elif b"OFF" in m:
                # videoin.stop()
                videoinstat = False
            elif b"STATUS" in m:
                client.publish(TOPIC, str(m.split(b":")[0])[2:-1]+("ON" if videoinstat else "OFF"))
                raise IndexError
        elif b"VIDEOOUT" in m:
            if b"ON" in m:
                # videoout.start()
                pass
            elif b"OFF" in m:
                # videoout.stop()
                pass
    except IOError:
        client.publish(TOPIC, str(m.split(b":")[0])[2:-1]+":"+"FAIL")
    except IndexError:
        pass
    else:
        client.publish(TOPIC, str(m.split(b":")[0])[2:-1]+":"+"ACK")

c.on_message = on_message
c.loop_forever()
