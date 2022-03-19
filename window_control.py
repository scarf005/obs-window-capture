import re
from dataclasses import dataclass
from os import system
from pathlib import Path
from subprocess import run
from typing import List

import psutil

int16 = lambda x: int(x, 16)


@dataclass
class WMClass:
    name: str
    class_: str

    @classmethod
    def from_string(cls, s):
        return cls(*s.split("."))


@dataclass
class Window:
    windowID: int
    desktopNum: int
    pid: int
    wmClass: WMClass
    title: str

    def __post_init__(self):
        self.windowID = int16(self.windowID)
        self.desktopNum = int(self.desktopNum)
        self.pid = int(self.pid)
        self.wmClass = WMClass.from_string(self.wmClass)

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
                f"{w.windowID:10} |{w.desktopNum:>3}  |{w.pid:>6} |"
                f" {w.wmClass.name:<8} | {w.title}"
            )

        return "Window ID  | Num |  PID  | WM_CLASS | Title\n" + "\n".join(
            [format_Window(w) for w in self._list]
        )


def create_windowlist() -> WindowList:
    def create_window(line: str) -> Window:
        windowID, desktopNum, pid, wm_class, _, title = re.split(
            r"\s+", line, maxsplit=5
        )
        return Window(windowID, desktopNum, pid, wm_class, title)

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
        print(window.wmClass)
        # print(window.executable_path)
