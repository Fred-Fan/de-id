import os
import random
import argparse
import glob
from shutil import copy2

def picking(finpath, pick_number, if_recursive):
    try:
        print("getting the directories..." )
        if if_recursive:
            filelist = glob.glob(finpath+"/**/*.txt", recursive=True)
        else:
            filelist = glob.glob(finpath+"/*.txt")
        print("Done, copy will begin.")
        return random.sample(filelist, pick_number)
    except ValueError:
        print("picking number is larger than the actual file number.")
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
                    help="Path to the directory or the file that contains the PHI note.")
    ap.add_argument("-r", "--recursive", action = 'store_true', default=False,
                    help="whether read files in the input folder recursively. Default is false.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory that save the randomly picked notes.")
    ap.add_argument("-n", "--number", required=True, type=int,
                    help="How many files you want to pick?:")
    args = ap.parse_args()

    finpath = args.input
    foutpath = args.output
    pick_number = args.number
    if_recursive = args.recursive
    if_dir = os.path.isdir(finpath)

    if if_dir:
        filelist = picking(finpath, pick_number, if_recursive)
        if not os.path.exists(foutpath) and filelist != []:
            print("Output folder does not exist. Will create one.")
            os.mkdir(foutpath)
        for i in filelist:
            copy2(i, foutpath)
            print("Copied",i,"to",foutpath)
    else:
        print("Input folder does not exist.")

if __name__ == "__main__":
    main()