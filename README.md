# Graphcord
Graphcord allows you to take your discord data and graph your messages over time

## Download
```sh
git clone https://github.com/Atli-A/Graphcord.git

cd Graphcord
```

## Usage
Make sure you have python3 installed as well as matplotlib

To run graphcord download it and run 
```sh
python3 graphcord.py path/to/your/data/package.zip
```
On Windows use the following:
```sh
python graphcord.py path/to/your/data/package.zip
```

## Flags
```
usage: graphcord.py [-h] [-n numlines] [-s startafter] [-l] [-u user [user ...]] [--hmms] [-w WORDS [WORDS ...]] FILE

Graph discord messages over time

positional arguments:
  FILE                  The path to your data package in its .zip format

optional arguments:
  -h, --help            show this help message and exit
  -n numlines           The top n users to graph
  -s startafter, --skip startafter
                        Skip the first n top users
  -l, --list            List all DMs to stdout and exit
  -u user [user ...], --user user [user ...]
                        Show only the given users data. Works with --hmms and ---words
  --hmms                Show statistics for words like hmm, huh, or lol
  -w WORDS [WORDS ...], --words WORDS [WORDS ...]
                        Show statistics for words of your choice. Supports regex (buggy)
```



## Example
![Example Graph](./screenshots/example1.png)
