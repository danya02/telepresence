#!/usr/bin/python3
import curses
import random
import paho.mqtt.client as mqtt
# import magic.input.keyboard as keys
# import magic.video.transmitter as videoout
# import magic.video.reciever as videoin
SERVER = "127.0.0.1"
TOPIC = "drone1"
c = mqtt.Client()
c.connect(SERVER)
c.subscribe(TOPIC)
global in_progress
in_progress = []
global done
done = []
global failed
done = []
global commands
commands = []


def gen_command(*comm):
    global commands
    command = hex(random.randint(0, 4294967295))[2:].upper()
    for i in comm:
        command += ":"
        command += i.upper()
    commands += [command]
    return command


def mainloop(stdscr):
    key = None
    client = c
    global distat
    # key = keys.getch()
    if key == "^[[A":
        client.publish(gen_command("move", "forward"), TOPIC)
    elif key == "^[[B":
        client.publish(gen_command("move", "back"), TOPIC)
    elif key == "^[[C":
        client.publish(gen_command("move", "right"), TOPIC)
    elif key == "^[[D":
        client.publish(gen_command("move", "left"), TOPIC)
    elif key == " ":
        client.publish(gen_command("ack"), TOPIC)
    elif key == "R":
        client.publish(gen_command("reboot"), TOPIC)
    elif key == "!":
        client.publish(gen_command("powercycle"), TOPIC)
    elif key == "D":
        client.publish(gen_command("display", "off" if distat else "on"), TOPIC)


def on_message(client, userdata, m):
    global in_progress
    global done
    global failed
    global distat
    global motorstat
    global alive
    m = m.payload.split(":")
    if "RACK" in m:
        print("Drone is alive.")
        alive = True
    elif "ACK" in m:
        in_progress.remove(m[0])
        done.append(m[0])
    elif "FAIL" in m:
        print("Command", m[1:], "failed.")
        in_progress.remove(m[0])
        failed.append(m[0])
    elif "DEAD" in m:
        print("Drone is dead.")
        alive = False
    elif "ALIVE" in m:
        print("Drone is alive.")
        alive = True
    else:
        for i in commands:
            if m[0] in i:
                break
        i = i.split(":")
        if i[1] == "DISPLAY":
            distat = True if m[1] == "ON" else False
        elif i[1] == "MOTORSTAT":
            motorstat = m[1]


curses.wrapper(mainloop)
