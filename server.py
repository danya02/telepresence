#!/usr/bin/python3
import gpiozero
# import magic.video.transmitter as videoout
# import magic.video.reciever as videoin
import paho.mqtt.client as mqtt
import os
import time
SERVER = "127.0.0.1"
TOPIC = "client1"
base.init()
global motorstat
motorstat = "STOP"
global base
base = gpiozero.Robot(left=(5, 6), right=(7, 8))
global display_relay
display_relay = gpiozero.LED(3)
kill_switch = gpiozero.LED(4, initial_value=True)
c = mqtt.Client()
c.will_set(TOPIC, payload="DEAD", qos=2)
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
        if "ACK" in m:
            client.publish(m.split(":")[0]+":"+"RACK", TOPIC)
            raise IndexError
        elif "MOVE" in m:
            if "FORWARD" in m:
                base.forward()
                motorstat = "FORWARD"
            elif "BACK" in m:
                base.back()
                motorstat = "BACK"
            elif "LEFT" in m:
                base.left()
                motorstat = "LEFT"
            elif "RIGHT" in m:
                base.right()
                motorstat = "RIGHT"
        elif "STOP" in m:
            base.stop()
            motorstat = "STOP"
        elif "MOTORSTAT" in m:
            client.publish(motorstat, TOPIC)
            raise IndexError
        elif "DISPLAY" in m:
            if "ON" in m:
                display_relay.on()
            elif "OFF" in m:
                display_relay.on()
            elif "STATUS" in m:
                client.publish("ON" if display_relay.is_lit else "OFF", TOPIC)
                raise IndexError
        elif "REBOOT" in m:
            os.popen("shutdown -r now")
            time.sleep(10)
            raise StandardError
        elif "POWERCYCLE" in m:
            kill_switch.off()
            time.sleep(5)
            raise StandardError
        elif "VIDEOIN" in m:
            if "ON" in m:
                # videoin.start()
                videoinstat = True
            elif "OFF" in m:
                # videoin.stop()
                videoinstat = False
            elif "STATUS" in m:
                client.publish("ON" if videoinstat else "OFF", TOPIC)
                raise IndexError
        elif "VIDEOOUT" in m:
            if "ON" in m:
                # videoout.start()
                pass
            elif "OFF" in m:
                # videoout.stop()
                pass
    except StandardError:
        client.publish(m.split(":")[0]+":"+"FAIL", TOPIC)
    except IndexError:
        pass
    else:
        client.publish(m.split(":")[0]+":"+"ACK", TOPIC)

c.on_message = on_message
c.loop_forever()
