#!/usr/bin/env python

import sys
import json

from attrs import define, field
import cattrs
import attrs
from enum import Enum
import typer
from typing_extensions import Annotated


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

    def row(self):
        return self.data.line_number

    def file(self):
        return self.data.path.text

    def text(self):
        return self.data.lines.text.rstrip()

    def column(self):
        return self.data.submatches[0].start + 1


def main(
        rows_before: Annotated[int, typer.Option("--rb")],
        lines_count: Annotated[int, typer.Option("--lc")],
):
    lines = sys.stdin.readlines()
    if len(lines) == 0:
        sys.exit(0)
    result = []
    for line in lines:
        value = json.loads(line)
        try:
            self = cattrs.structure(value, RGLine)
            # TODO: remove magic numbers
            row_start = max(self.row() - rows_before, 1)
            result.append(f"{self.file()}:{self.row()}:{self.column()}:{row_start}:{lines_count}:{self.text()}")
        except Exception as e:
            pass

    print("\n".join(result))


if __name__ == "__main__":
    typer.run(main)
