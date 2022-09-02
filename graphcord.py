#!/usr/bin/env python3

import sys
import datetime
import re
import os
import json
import csv
import tempfile
import zipfile
import argparse

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

hmms_pattern = re.compile(
r"""
^(
(?P<L>L)|
(?P<yup>yup|yep)|
(?P<heh>he(h+))|
(?P<huh>hu(h+))|
(?P<why>wh(y+))|
(?P<what>wh(a+)(t*))|
(?P<mhm>(m+)h(m+))|
(?P<hmm>h(m+))|
(?P<lol>l(o+)l)|
(?P<lmao>lm(f?)(a+)(o+))|
(?P<yes>ye(s*))|
(?P<no>n(o+))|
(?P<oh>(o+)(h*))
)$
""", re.IGNORECASE | re.MULTILINE | re.VERBOSE)

def find_hmms(pattern, string, hmms_dict):
    results = pattern.finditer(string)
    for found in results:
        hmm_found = None
        for name, value in found.groupdict().items():
            if value is not None:
                hmm_found = name

        if hmm_found is None:
            continue

        if hmm_found not in hmms_dict:
            hmms_dict[hmm_found] = 0
        hmms_dict[hmm_found] += 1

def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)

def get_dms(path):
    try:
        with open(os.path.join(path, "index.json"), encoding="utf-8") as f:
            names = json.load(f)
    except Exception:
        err("Could not find %s" % os.path.join(path, "index.json"))

    # generate list of dms
    #     channel id : name
    print("Collecting Names")
    dms = {}
    for i in os.listdir(path):
        if os.path.isdir(os.path.join(path, i)):
            with open(os.path.join(path, i, "channel.json"), encoding="utf-8") as file:
                if json.load(file)["type"] == 1:
                    name = names[i[1:]]
                    startstr = "Direct Message with "
                    dms[i] = name[len(startstr):] if name.startswith(startstr) else name
    return dms

def word_clean(word):
    bad_words = ["\\s", "\\d"]
    for i in bad_words:
        word = word.replace(i, "_")

    bad_letters = "*()?\"\\"
    for i in bad_letters:
        word = word.replace(i, "_")

    word = "PHRASE_%s" % word
    print(word)
    return word


def compile_words(words):
    buf = ""
    for i in words:
        print(i)
        buf += "(?P<%s>%s)|" % (word_clean(i), i)
    buf = buf[:-1] 
    print(buf)
    return re.compile(buf, re.IGNORECASE | re.MULTILINE | re.VERBOSE)

def read(path, args):
    path = os.path.join(path, "messages/")
    print("Finding DMs")
    dms = get_dms(path)
    print("Reading DMs")
    # for each dm read and plot
    leaders = {}
    pattern = hmms_pattern if args.words is None else compile_words(args.words)
        
    for directory, username in dms.items():
        msg_total = [1]
        timestamp = []
        hmms = []
        with open(os.path.join(path, directory, "messages.csv"), encoding="utf-8") as f:
            msgs = csv.reader(f)
            next(msgs) # skip the header
            msgs = reversed(list(msgs))
            hmms_dict = {}

            for line in msgs:
                date = line[1]
                timestamp.append(datetime.datetime.fromisoformat(date))
                msg_total.append(msg_total[-1] + 1)

                msg_content = line[2]
                find_hmms(pattern, msg_content, hmms_dict)
                hmms.append(hmms_dict.copy())
            msg_total = msg_total[1:]
            
            if len(msg_total) != 0:
                leaders[username] = [timestamp, msg_total, hmms]

    if args.list:
        total_total = 0
        for name, v in leaders.items():
            total_messages = v[1][-1]
            total_total += total_messages
            print(f"{name:<40} {total_messages:>10}")
        name = "Total"
        print(f"{name:<40} {total_total:>10}")
        return

    max_timestamp = max([max(v[0]) for _, v in leaders.items() if len(v[0]) != 0])

    for k, v in leaders.items():
        v[0].append(max_timestamp)
        v[1].append(v[1][-1])

    # transpose hmms into lists of counts
    for k, v in leaders.items():
        transposed_hmms = []
        hmms_list_of_dicts = v[2]
        hmm_types = hmms_list_of_dicts[-1].keys()
        for name in hmm_types:
             values = [hmm_dict.get(name, 0) for hmm_dict in hmms_list_of_dicts]
             values.append(values[-1])
             transposed_hmms.append((name, values))

        leaders[k][2] = transposed_hmms

    leaders = sorted(leaders.items(), key=lambda i: len(i[1][0]), reverse=True)

    if args.user:
        selected_users = list(filter(lambda item: any_in([i.lower() for i in args.user], item[0].lower()), leaders))
        if selected_users:
            leaders = selected_users
        else:
            print(f"Can't find a user named {args.user}, showing all", file=sys.stderr)

    start_after = args.startafter
    if start_after > len(leaders):
        print(f"Can't start after {start_after} users, you only have {len(leaders)}, starting at 0", file=sys.stderr)
        start_after = 0

    users_to_display = leaders[start_after:(start_after + args.numlines)]

    names = [user[0] for user in users_to_display]
    print(f"Showing data for user(s): {', '.join(names)}")

    for name, data in users_to_display:
        if args.hmms or args.words != None:
            if len(users_to_display) > 1:
                err("Can't show hmms for more than one user, please make your constraints more specific,\nRun with --list to see all users")
            for name, values in data[2]:
                plt.plot(data[0], values, "-", label=name)
        else:
            plt.plot(data[0], data[1], "-", label=name)


    # Graph stuff
    print("Plotting")
    plt.legend(loc="upper left")
    #plt.title("Top %d most messaged users over time" % args.numlines)
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

def any_in(lst1, lst2):
    for i in lst1:
        if i in lst2:
            return True
    return False

parser = argparse.ArgumentParser(description="Graph discord messages over time")
parser.add_argument("path", metavar="FILE", type=str, nargs=None, help="The top n users to graph")
parser.add_argument("-n", dest="numlines", metavar="numlines", type=uint, default=10, help="The top n users to graph")
parser.add_argument("-s", "--skip", dest="startafter", metavar="startafter", type=uint, default=0, help="Skip the first `start` top users")
parser.add_argument("-l", "--list" , dest="list", action="store_true", help="List all DMs and exit")
parser.add_argument("-u", "--user" , dest="user", metavar="user", type=str, nargs="+", default=None, help="Show only the given `user`")
parser.add_argument("--hmms" , dest="hmms", action="store_true", help="Show statistics for words like hmm, huh, or lol")
parser.add_argument("-w", "--words", nargs="+", dest="words", default=None, help="Graph words")

args = parser.parse_args()
if args.hmms and args.words:
    raise argparse.ArgumentTypeError("-w/--words cannot be used with --hmms")

path = args.path
if not os.path.isfile(path):
    err("No file %s" % path)

zf = zipfile.ZipFile(path, "r")

with tempfile.TemporaryDirectory() as tf:
    print("Extracting")
    zf.extractall(tf)
    # ensure we have ma messages dir
    if "messages" not in os.listdir(tf):
        err("No \"messages\" directory found in file")
    read(tf, args)
