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
    
    atfs = [ Atf(f"{atf_pth}/{file_name}") for file_name in contains if file_name.endswith(".atf") ]
    
    