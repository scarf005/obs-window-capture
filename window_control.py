import re
from dataclasses import dataclass
from os import system
from pathlib import Path
from subprocess import run
from typing import List

import psutil

int16 = lambda x: int(x, 16)


@dataclass
class Window:
    id: int
    desktopNum: int
    pid: int
    wm_class: str
    title: str

    def __post_init__(self):
        self.id = int16(self.id)
        self.desktopNum = int(self.desktopNum)
        self.pid = int(self.pid)

    @property
    def executable_path(self) -> str:
        return psutil.Process(self.pid).exe()


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

    capture = run(["wmctrl", "-l", "-p", "-u", "-x"], capture_output=True)
    lines = capture.stdout.decode().splitlines()
    return WindowList([create_window(line) for line in lines])


# for line in capture.splitlines():
# print(re.split(r"\s+", line, maxsplit=4))

if __name__ == "__main__":
    window_list = create_windowlist()
    print(window_list)
    for window in window_list:
        # print(window)
        print(window.executable_path)
