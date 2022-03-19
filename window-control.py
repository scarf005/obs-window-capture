import re
from dataclasses import dataclass
from pathlib import Path
from subprocess import PIPE, run
from textwrap import shorten
from typing import List

import attr
from pyparsing import col

int16 = lambda x: int(x, 16)


@dataclass
class Window:
    id: int = attr.field(converter=int16)
    desktopNum: int = attr.field(converter=int)
    pid: int = attr.field(converter=int)
    wm_class: str = attr.field()
    title: str = attr.field()


@dataclass
class WindowList:
    _list: List[Window]

    def __iter__(self):
        return iter(self._list)

    def __str__(self) -> str:
        def truncate(column: str):
            return column[:7] + "…" if len(column) > 8 else column

        def format_Window(w: Window) -> str:
            return (
                f"{w.id:10} |{w.desktopNum:>3}  |{w.pid:>6} |"
                f" {truncate(w.wm_class.split('.')[1]):<8} | {w.title}"
            )

        return "Window ID  | Num |  PID  | WM_CLASS | Title\n" + "\n".join(
            [format_Window(w) for w in self._list]
        )


def create_windowlist() -> WindowList:
    def create_window(line: str) -> Window:
        return Window(*re.split(r"\s+", line, maxsplit=4))

    capture = run(["wmctrl", "-l", "-p", "-u", "-x"], stdout=PIPE)
    lines = capture.stdout.decode().splitlines()
    return WindowList([create_window(line) for line in lines])


# for line in capture.splitlines():
# print(re.split(r"\s+", line, maxsplit=4))

if __name__ == "__main__":
    window_list = create_windowlist()
    print(window_list)
    for window in window_list:
        print(window)
