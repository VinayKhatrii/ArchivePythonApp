import sys

paths = ["./main_files", "./site-packages"]
sys.path.extend(paths)

from start import main
