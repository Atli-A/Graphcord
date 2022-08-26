#!/usr/bin/env python3

import sys
import datetime
import os
import json
import tempfile
import zipfile
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)

def read(path, numlines):
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
                name = names[i[1:]] 
                startstr = "Direct Message with"
                dms[i] = name[len(startstr):] if name.startswith(startstr) else name

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
        if i > numlines:
            break
        plt.plot(d[0], d[1], "-", label=n)

    print("Plotting")
    plt.legend( loc="upper left")
    plt.title("Top %d most messaged users over time" % numlines)
    plt.ylabel("Messages")
    plt.xlabel("Date")
    plt.xticks(rotation=75)
    plt.tight_layout()
    plt.show()

parser = argparse.ArgumentParser(description="Graph discord messages over time")
parser.add_argument("path", metavar="path", type=str, nargs=None, help="The top n users to graph")
parser.add_argument("-n", metavar="numlines", type=int, nargs=1, default=[10], help="The top n users to graph")
args = parser.parse_args()

path = args.path
if not os.path.isfile(path):
    err("No file %s" % path)

zf = zipfile.ZipFile(path, "r")

with tempfile.TemporaryDirectory() as tf:
    print("Extracting")
    zf.extractall(tf)
    read(tf, args.n[0])
