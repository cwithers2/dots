#!/usr/bin/env python3
import argparse
import urllib.parse

address = "https://www.duckduckgo.com/?"
bangs = {
    "DuckDuckGo"      : "!?",
    "Google"          : "!g",
    "Wikipedia"       : "!w",
    "Amazon"          : "!a",
    "StackOverflow"   : "!ov",
    "YouTube"         : "!yt",
    "Python3 Docs"    : "!py3",
    "C++ Ref"         : "!cpp",
    "Reddit"          : "!r",
    "GitHub"          : "!github",
    "Arch Linux Wiki" : "!aw"
}
default = "DuckDuckGo"

def sort_key(value):
    if value == default:
        return ""
    else:
        return value

def url(key, query):
    params = { "q" : f"{bangs[key]} {query}"}
    return f"{address}{urllib.parse.urlencode(params)}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", dest="keys", action="store_const", const=1)
    parser.add_argument("--url", type=str, nargs=2, metavar=("key", "query"))
    args = parser.parse_args()
    if bool(args.keys) == bool(args.url): # XNOR gate ie !(a xor b)
        parser.print_help()
        raise SystemExit(0)
    if args.keys:
        for k in sorted(bangs, key=sort_key):
            print(k)
    else:
        print(url(args.url[0], args.url[1]))
