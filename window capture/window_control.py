import re
from dataclasses import dataclass
from subprocess import run
from typing import List

import psutil


def int16(n: str) -> int:
    return int(n, 16)


@dataclass
class WMClass:
    name: str
    class_: str

    @classmethod
    def from_string(cls, s: str):
        arr = s.split(".")
        if len(arr) != 2:
            return cls(s, s)
        else:
            return cls(*arr)


class Window:
    def __init__(
        self,
        raw_windowID: str,
        raw_desktopNum: str,
        raw_pid: str,
        raw_wmClass: str,
        title: str,
    ):
        self.windowID = int16(raw_windowID)
        self.desktopNum = int(raw_desktopNum)
        self.pid = int(raw_pid)
        self.wmClass = WMClass.from_string(raw_wmClass)
        self.title = title

    @property
    def executable_path(self) -> str:
        try:
            return psutil.Process(self.pid).exe()
        except (PermissionError, psutil.AccessDenied) as e:
            return f"(Not accessible: {e})"

    def __repr__(self) -> str:
        return (
            f"{self.windowID:10} |{self.desktopNum:>3}  |{self.pid:>6} |"
            f" {self.wmClass.name:<13} | {self.title}"
        )


@dataclass
class WindowList:
    _list: List[Window]

    def __iter__(self):
        return iter(self._list)

    def detailed(self) -> str:
        return (
            "Window ID  | Num |  PID  | WM_CLASS      | Title\n"
            + "\n".join(str(w) for w in self._list)
        )

    def __str__(self) -> str:
        title_len = max(len(w.title) for w in self._list) + 1
        executable_len = max(len(w.executable_path) for w in self._list) + 1

        return (
            f"{'Executable Path':<{executable_len}}|{'Title':<{title_len}}\n"
            f"{'-' * executable_len}+{'-' * title_len}\n"
            + "\n".join(
                f"{w.executable_path:<{executable_len}}|{w.title:<{title_len}}"
                for w in self._list
            )
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
