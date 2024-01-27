#!/usr/bin/env python

import sys

def main():
    lines = sys.stdin.readlines()
    if len(lines) == 0:
        sys.exit(0)
    line = lines[0]
    result = line.split(":")
    file = result[0]
    line = result[1]
    column = result[2].strip()

    print(f""" +"call cursor({line}, {column})" "{file}" """)
