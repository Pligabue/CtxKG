import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--small", dest="size", action="store_const", const="small")
parser.add_argument("--medium", dest="size", action="store_const", const="medium")
parser.add_argument("--big", dest="size", action="store_const", const="big")
parser.add_argument("-c", "--clean", dest="clean", action="store_true")
parser.add_argument("-r", "--ratio", type=float, default=1.0)
parser.add_argument("-t", "--threshold", type=float, default=0.8)
parser.add_argument("-l", "--language", type=str, default="en")
parser.add_argument("-n", "--name", type=str)
parser.add_argument("-b", "--batch", type=int, default=300)
parser.set_defaults(size="small", clean=False)
args = parser.parse_args()

SIZE = args.size
CLEAN = args.clean
RATIO = args.ratio
THRESHOLD = args.threshold
LANGUAGE = args.language
NAME = args.name
BATCH_SIZE = args.batch
