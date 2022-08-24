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
    sys.exit(1)

def read(path):
    if "messages" not in os.listdir(path):
        err("No \"messages\" directory found in file")

    path = os.path.join(path, "messages/")

    try:
        names = json.loads(open(os.path.join(path, "index.json")).read())
    except Exception:
        err("Could not find %s" % os.path.join(path, "index.json"))

    # generate list of dms
    #     channel id : name
    print("Collecting Names")
    dms = {}
    for i in os.listdir(path):
        if os.path.isdir(os.path.join(path, i)): 
            if json.loads(open(os.path.join(path, i, "channel.json")).read())["type"] == 1:
                dms[i] = names[i[1:]]

    print("Reading DMs")
    # for each dm read and plot
    leaders = {}
    for k, v in dms.items():
        msg_total = []
        timestamp = []
        msgs = open(os.path.join(path, k, "messages.csv"))
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
        if len(msg_total) != 0:
            leaders[v] = (timestamp, msg_total)
    max_timestamp = max([max(v[0]) for _, v in leaders.items() if len(v[0]) != 0])

    for k, v in leaders.items():
        v[0].append(max_timestamp)
        v[1].append(v[1][-1])

    leaders = dict(sorted(leaders.items(), key=lambda i: len(i[1][0]), reverse=True))
    i = 0
    for n, d in leaders.items():
        i += 1
        if i > 10:
            break
        plt.plot(d[0], d[1], "-", label=n)

    print("Plotting")
    plt.legend( loc="upper left")

    plt.ylabel("Messages")
    plt.xlabel("Date")
    plt.show()

if len(sys.argv) != 2:
    err("Expects one argument: the path to the discord data download")

path = sys.argv[1]

if not os.path.isfile(path):
    err("No file %s" % path)

zf = zipfile.ZipFile(path, "r")

with tempfile.TemporaryDirectory() as tf:
    print("Extracting")
    zf.extractall(tf)
    read(tf)
