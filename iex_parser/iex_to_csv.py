"""Convert an IEX file to CSV files"""

import argparse


def parse_args(args):
    parser = argparse.ArgumentParser(description='Short sample app')

    parser.add_argument('-a', action="store_true", default=False)
    parser.add_argument('-b', action="store", dest="b")
    parser.add_argument('-c', action="store", dest="c", type=int)

    return parser.parse_args(args)


def iex_to_csv():
    pass
