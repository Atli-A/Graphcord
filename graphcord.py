#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import datetime
import os
import json
import tempfile
import zipfile

def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def read(path):
    if "messages" not in os.listdir(path):
        err("No \"messages\" directory found in file")
        sys.exit(1)

    path = os.path.join(path, "messages/")

    try:
        names = json.loads(open(path + "index.json").read())
    except Exception:
        err("Could not find %s" % path + "index.json")
        sys.exit(1)

    # generate list of dms
    #     channel id : name
    print("Collecting Names")
    dms = {}
    for i in os.listdir(path):
        if os.path.isdir(path + i): 
            if json.loads(open(path + i + "/channel.json").read())["type"] == 1:
                dms[i] = names[i[1:]]

    print("Reading DMs")
    # for each dm read and plot
    for k, v in dms.items():
        msg_total = []
        timestamp = []
        msgs = open(path + k + "/messages.csv")
        msgs = msgs.read().split(",\n")[1:]
        msgs.reverse()
        for i in msgs: # skip first line
            try:
                date = i.split(",")[1]
                timestamp.append(datetime.datetime.fromisoformat(date))
            except Exception:
                continue
            if len(msg_total) == 0:
                msg_total.append(1)
            else:
                msg_total.append(msg_total[-1] + 1)
        if len(msgs) > 1000:
            plt.plot(timestamp, msg_total, "-", label=v)

    print("Plotting")
    plt.legend( loc="upper left")

    plt.ylabel("Messages")
    plt.xlabel("Date")
    plt.show()




if len(sys.argv) != 2:
    err("Expects one argument: the path to the discord data download")
    sys.exit(1)

path = sys.argv[1]

if not os.path.isfile(path):
    err("No file %s" % path)
    sys.exit(1)

zf = zipfile.ZipFile(path, "r")

with tempfile.TemporaryDirectory() as tf:
    print("Extracting")
    zf.extractall(tf)
    read(tf)


