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

def read(path, numlines, start_after):
    if "messages" not in os.listdir(path):
        err("No \"messages\" directory found in file")

    path = os.path.join(path, "messages/")

    try:
        f =open(os.path.join(path, "index.json")
        names = json.load(f)
        f.close()
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

    if start_after > len(leaders):
        print(f"Can't start after {start_after} users, you only have {len(leaders)}, starting at 0", file=sys.stderr)
        start_after = 0

    leaders_to_display = list(leaders.items())[start_after:start_after + numlines]

    for name, data in leaders_to_display:
        plt.plot(data[0], data[1], "-", label=name)

    print("Plotting")
    plt.legend( loc="upper left")
    plt.title("Top %d most messaged users over time" % numlines)
    plt.ylabel("Messages")
    plt.xlabel("Date")
    plt.xticks(rotation=75)
    plt.tight_layout()
    plt.show()

def uint(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid, need a positive int value" % value)
    return ivalue

parser = argparse.ArgumentParser(description="Graph discord messages over time")
parser.add_argument("path", metavar="path", type=str, nargs=None, help="The top n users to graph")
parser.add_argument("-n", metavar="numlines", type=uint, nargs=1, default=[10], help="The top n users to graph")
parser.add_argument("--start", metavar="start", type=uint, nargs=1, default=[0], help="Skip the first `start` top users")
args = parser.parse_args()

path = args.path
if not os.path.isfile(path):
    err("No file %s" % path)

zf = zipfile.ZipFile(path, "r")

with tempfile.TemporaryDirectory() as tf:
    print("Extracting")
    zf.extractall(tf)
    read(tf, args.n[0], args.start[0])
