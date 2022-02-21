import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from olympus import Athena

if __name__ == "__main__":
    csv_path = sys.argv[1]
    Athena().run(csv_path)