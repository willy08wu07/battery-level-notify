#!/usr/bin/env python3

# TODO: 這是臨時寫的版本，未來應透過狀態圖釐清所有狀態再重構

import re
import subprocess


is_charging_excepted = True


def fetch_percentage() -> int:
    process = subprocess.run([
            'upower',
            '-i',
            '/org/freedesktop/UPower/devices/battery_BAT0'
        ],
        text=True,
        stdout=subprocess.PIPE,
    )
    p = re.compile(r'.*^\s*percentage:\s*(\d+)%$.*', re.MULTILINE | re.DOTALL)
    match = p.match(process.stdout)
    assert match
    percentage = int(match.group(1))
    return percentage


def determine_notify(percentage: int) -> None:
    global is_charging_excepted
    if is_charging_excepted and percentage >= 100:
        is_charging_excepted = False
        subprocess.run([
            'notify-send',
            "充電完成",
            "電量達到 100%，請拔除插頭。",
        ])
    if not is_charging_excepted and percentage == 96:
        is_charging_excepted = True
        subprocess.run([
            'notify-send',
            "放電完成",
            "電量剩餘 96%，請插入插頭。",
        ])


def wait_stat_change() -> bool:
    global monitor
    monitor.stdout.readline()
    return True


percentage = fetch_percentage()
determine_notify(percentage)

monitor = subprocess.Popen(
    ['upower', '-m'],
    stdout=subprocess.PIPE,
    text=True,
)
while wait_stat_change():
    percentage = fetch_percentage()
    determine_notify(percentage)
