import argparse

from ...constants import DEFAULT_PARAMS


parser = argparse.ArgumentParser()
parser.add_argument("--small", dest="size", action="store_const", const="small")
parser.add_argument("--medium", dest="size", action="store_const", const="medium")
parser.add_argument("--big", dest="size", action="store_const", const="big")
parser.add_argument("-r", "--ratio", type=float, default=DEFAULT_PARAMS["base"]["ratio"])
parser.add_argument("-t", "--threshold", type=float, default=DEFAULT_PARAMS["base"]["threshold"])
parser.add_argument("-l", "--language", type=str, default="en")
parser.add_argument("-n", "--name", type=str)
parser.add_argument("-b", "--batch", type=int, default=DEFAULT_PARAMS["base"]["batch_size"])
parser.set_defaults(size="small")
args = parser.parse_args()

SIZE = args.size
RATIO = args.ratio
THRESHOLD = args.threshold
LANGUAGE = args.language
NAME = args.name
BATCH_SIZE = args.batch
