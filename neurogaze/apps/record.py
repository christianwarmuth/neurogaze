"""Log window focus and appearance.

Credit to Kevin Turner for consolidated windows event handling:
https://gist.github.com/keturn/6695625

Much credit to Eric Blade for this:
https://mail.python.org/pipermail/python-win32/2009-July/009381.html
and David Heffernan:
http://stackoverflow.com/a/15898768/9585
"""

import sys
import ctypes
import ctypes.wintypes
import time
import json
from contextlib import contextmanager
from collections import defaultdict

import win32con


class Counter:

    def __init__(self, initial_value=-1):
        self.value = initial_value

    def __call__(self):
        self.value += 1
        return self.value


def create_encoding_dict(name):
    try:
        with open(f'{name}.json', 'r') as f:
            existing_encoding = json.load(f)
    except FileNotFoundError:
        existing_encoding = {}

    initial_id = max(list(existing_encoding.values()) + [-1])

    return defaultdict(Counter(initial_id), existing_encoding)


user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)


# The types of events we want to listen for, and the names we'll use for
# them in the log output. Pick from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
eventTypes = {
    win32con.EVENT_SYSTEM_FOREGROUND: "Foreground",
    win32con.EVENT_OBJECT_FOCUS: "Focus",
    # win32con.EVENT_OBJECT_SHOW: "Show",
    win32con.EVENT_SYSTEM_DIALOGSTART: "Dialog",
    win32con.EVENT_SYSTEM_CAPTURESTART: "Capture",
    win32con.EVENT_SYSTEM_MINIMIZEEND: "UnMinimize",
    win32con.EVENT_SYSTEM_MOVESIZEEND: "Resize",
}

processFlag = getattr(
    win32con, 'PROCESS_QUERY_LIMITED_INFORMATION',
    win32con.PROCESS_QUERY_INFORMATION
)

threadFlag = getattr(
    win32con, 'THREAD_QUERY_LIMITED_INFORMATION',
    win32con.THREAD_QUERY_INFORMATION
)


def log_error(msg):
    sys.stdout.write(msg + '\n')


def get_process_id(dw_event_thread, hwnd):
    h_thread = kernel32.OpenThread(threadFlag, 0, dw_event_thread)

    if h_thread:
        try:
            process_id = kernel32.GetProcessIdOfThread(h_thread)
            if not process_id:
                log_error(
                    "Couldn't get process for thread "
                    f"{h_thread}: {ctypes.WinError()}"
                )
        finally:
            kernel32.CloseHandle(h_thread)
    else:
        errors = [
            f"No thread handle for {dw_event_thread}: {ctypes.WinError()}"]

        if hwnd:
            process_id = ctypes.wintypes.DWORD()
            thread_id = user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(process_id))
            if thread_id != dw_event_thread:
                log_error(
                    "Window thread != event thread? "
                    f"{thread_id} != {dw_event_thread}"
                )
            if process_id:
                process_id = process_id.value
            else:
                errors.append(
                    f"GetWindowThreadProcessID({hwnd}) didn't work either: "
                    "{ctypes.WinError()}"
                )
                process_id = None
        else:
            process_id = None

        if not process_id:
            for err in errors:
                log_error(err)

    return process_id


def get_process_filename(process_id):
    hProcess = kernel32.OpenProcess(processFlag, 0, process_id)
    if not hProcess:
        log_error(f"OpenProcess({process_id}) failed: {ctypes.WinError()}")
        return None

    try:
        filenameBufferSize = ctypes.wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filenameBufferSize.value)
        kernel32.QueryFullProcessImageNameW(
            hProcess, 0, ctypes.byref(filename),
            ctypes.byref(filenameBufferSize)
        )

        return filename.value
    finally:
        kernel32.CloseHandle(hProcess)


def setHook(WinEventProc, eventType):
    return user32.SetWinEventHook(
        eventType,
        eventType,
        0,
        WinEventProc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )


class Callback:

    def __init__(self, filename):
        self.filename = filename
        self.windows_apps = create_encoding_dict(f'{filename}.apps.json')
        self.windows_tabs = create_encoding_dict(f'{filename}.tabs.json')
        self.last_windows_apps_size = len(self.windows_apps)
        self.last_windows_tabs_size = len(self.windows_tabs)

    @contextmanager
    def get_callback(self):
        with open(self.filename, 'w') as f, \
                open(f'{self.filename}.apps.json', 'w') as apps, \
                open(f'{self.filename}.tabs.json', 'w') as tabs:

            def callback(
                hWinEventHook,
                event,
                hwnd,
                idObject,
                idChild,
                dw_event_thread,
                dwmsEventTime
            ):
                length = user32.GetWindowTextLengthW(hwnd)
                title = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, title, length + 1)

                process_id = get_process_id(dw_event_thread, hwnd)

                short_name = '?'
                if process_id:
                    filename = get_process_filename(process_id)
                    if filename:
                        short_name = '\\'.join(filename.rsplit('\\', 2)[-2:])

                short_name_id = self.windows_apps[short_name]
                title_id = self.windows_tabs[title.value]

                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))

                timestamp = time.time()

                csv_values = ','.join([str(x) for x in (
                    timestamp,
                    eventTypes.get(event, hex(event)),
                    short_name_id,
                    title_id,
                    rect.left,
                    rect.top,
                    rect.right,
                    rect.bottom,
                )])
                f.write(f'{csv_values}\n')
                f.flush()

                if self.last_windows_apps_size < len(self.windows_apps):
                    apps.seek(0)
                    json.dump(self.windows_apps, apps)
                    apps.truncate()

                    apps.flush()

                if self.last_windows_tabs_size < len(self.windows_tabs):
                    tabs.seek(0)
                    json.dump(self.windows_tabs, tabs)
                    tabs.truncate()

                    tabs.flush()

                self.last_windows_apps_size = len(self.windows_apps)
                self.last_windows_tabs_size = len(self.windows_tabs)

            yield callback


def main(filename):
    ole32.CoInitialize(0)
    t = Callback(filename)
    with t.get_callback() as callback:
        WinEventProc = WinEventProcType(callback)
        user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

        hookIDs = [setHook(WinEventProc, et) for et in eventTypes.keys()]
        if not any(hookIDs):
            print('SetWinEventHook failed')
            sys.exit(1)

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessageW(msg)
            user32.DispatchMessageW(msg)

        for hookID in hookIDs:
            user32.UnhookWinEvent(hookID)
        ole32.CoUninitialize()


if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        filename = 'windows_data.log'

    main(filename)
