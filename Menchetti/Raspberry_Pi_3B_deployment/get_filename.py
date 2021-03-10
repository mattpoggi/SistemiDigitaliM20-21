#!/usr/bin/python

import argparse
import os

parser = argparse.ArgumentParser(description='Get filename')
parser.add_argument('--dir', type=str, required=True, help='cartella per uploads')
args = parser.parse_args()

num_files = len([name for name in os.listdir(args.dir) if os.path.isfile(os.path.join(args.dir, name))])

print(str(num_files).zfill(3))
