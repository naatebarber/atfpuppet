import sys
import os
from pathlib import Path
from read_atf import Atf

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: /path/to/main.py /path/to/atf_folder")
        exit(0)

    atf_pth = sys.argv[1]
    print(atf_pth)

    contains = os.listdir(atf_pth)

    atfs = [
        Atf(f"{atf_pth}/{file_name}")
        for file_name in contains
        if file_name.endswith(".atf")
    ]

    test_atf = atfs[0]

    test_atf.reshape({"start_time": 4, "end_time": 5, "peak_amp": 7})

    test_atf.reshape_transform("start_time", lambda x: float(x) / 1000)
    test_atf.reshape_transform("end_time", lambda x: float(x) / 1000)
    test_atf.reshape_transform("peak_amp", lambda x: abs(float(x)))

    iei = [0]

    start_time = test_atf.reshape_get("start_time")
    end_time = test_atf.reshape_get("end_time")

    for ix in range(1, len(start_time)):
        iei_value = start_time[ix] - end_time[ix - 1]
        iei.append(iei_value)

    test_atf.reshape_add_field("iei", iei)

    print(test_atf.reshaped)
