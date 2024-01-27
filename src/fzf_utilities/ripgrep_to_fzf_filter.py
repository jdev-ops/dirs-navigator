#!/usr/bin/env python

import sys
import json

from attrs import define, field
import cattrs
import attrs
from enum import Enum

# @unique
class MatchType(Enum):
    BEGIN = "begin"
    MATCH = "match"
    END = "end"

@define
class Path:
    text: str = field(
        validator=attrs.validators.instance_of(str)
    )


@define
class Line:
    text: str = field(
        validator=attrs.validators.instance_of(str)
    )

@define
class Submatch:
    start: int = field(
        validator=attrs.validators.instance_of(int)
    )

@define
class Match:
    path: Path = field(
        validator=attrs.validators.instance_of(Path)
    )
    lines: Line = field(
        validator=attrs.validators.instance_of(Line)
    )
    line_number: int = field(
        validator=attrs.validators.instance_of(int)
    )
    submatches: list[Submatch] = field(
    )

@define
class RGLine:
    type: MatchType = field(
        validator=attrs.validators.instance_of(MatchType)
    )
    data: Match = field(
        validator=attrs.validators.instance_of(Match)
    )
    def line(self):
        return self.data.line_number

    def file(self):
        return self.data.path.text

    def text(self):
        return self.data.lines.text.rstrip()

    def column(self):
        return self.data.submatches[0].start + 1

    def __str__(self):
        return f"{self.file()}:{self.line()}:{self.column()}:{self.text()}"

def main():
    lines = sys.stdin.readlines()
    if len(lines) == 0:
        sys.exit(0)
    result=[]
    for line in lines:
        value = json.loads(line)
        try:
            line = cattrs.structure(value, RGLine)
            result.append(str(line))
        except Exception as e:
            pass

    print("\n".join(result))
