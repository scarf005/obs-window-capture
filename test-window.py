
import re
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, run
from typing import List

import attr

int16 = lambda x: int(x, 16)


@dataclass
class Window:
    id: int = attr.field(converter=int16)
    desktopNum: int = attr.field(converter=int)
    pid: int = attr.field(converter=int)
    wm_class: str = attr.field()
    title: str = attr.field()

WindowList = List[Window]


def create_windowlist() -> WindowList:
    def create_window(line: str) -> Window:
        return Window(*re.split(r"\s+", line, maxsplit=4))

    capture = run(["wmctrl", "-l", "-p", "-u", "-x"], stdout=PIPE)
    lines = capture.stdout.decode().splitlines()
    return [create_window(line) for line in lines]


# for line in capture.splitlines():
# print(re.split(r"\s+", line, maxsplit=4))

for window in create_windowlist():
    print(window)
