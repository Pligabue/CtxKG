import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold", type=float, default=0.8)
parser.add_argument("--small", dest="size", action="store_const", const="small")
parser.add_argument("--medium", dest="size", action="store_const", const="medium")
parser.add_argument("--big", dest="size", action="store_const", const="big")
parser.add_argument("-o", "--overwrite", dest="overwrite", action="store_true")
parser.add_argument("-c", "--clean", dest="clean", action="store_true")
parser.add_argument("-r", "--ratio", type=float, default=1.0)
parser.add_argument("-m", "--match", type=str, default="*.txt")
parser.add_argument("-g", "--groups", type=int, default=1)
parser.set_defaults(size="small", overwrite=False, clean=False)
args = parser.parse_args()

THRESHOLD = args.threshold
SIZE = args.size
OVERWRITE = args.overwrite
RATIO = args.ratio
MATCH = args.match
GROUPS = args.groups
CLEAN = args.clean