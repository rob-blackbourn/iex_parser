"""Convert an IEX DEEP or TOPS files to JSON"""

import argparse
from datetime import datetime
from decimal import Decimal
import gzip
import json
import logging
from pathlib import Path
import sys
from typing import Any, Iterator, List, Mapping

from iex_parser import Parser, DEEP_1_0, TOPS_1_5, TOPS_1_6
from iex_parser.iex_to_csv import FILENAME_REGEX


class JSONEncoderEx(json.JSONEncoder):

    # pylint: disable=arguments-differ,method-hidden
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.decode()
        else:
            return json.JSONEncoder.default(self, obj)


def convert(filename: Path, output_path: Path, tickers: List[bytes], is_silent: bool):
    matches = FILENAME_REGEX.match(filename.name)

    if not matches:
        raise ValueError('Unable to process filename')

    dct = matches.groupdict()
    start_date = datetime.strptime(dct['start_date'], '%Y%m%d')
    end_date = datetime.strptime(dct['end_date'], '%Y%m%d')
    protocol = dct['protocol']
    feed = dct['feed']
    version = dct['version']

    if output_path.is_dir():
        json_filename = f'data_feed_{start_date:%Y%m%d}_{end_date:%Y%m%d}_{protocol}_{feed}{version}.json.gz'
        output_path = output_path / json_filename

    if feed == 'DEEP'and version == '1.0':
        feed_def = DEEP_1_0
    elif feed == 'TOPS' and version == '1.5':
        feed_def = TOPS_1_5
    elif feed == 'TOPS' and version == '1.6':
        feed_def = TOPS_1_6
    else:
        raise ValueError(f'Unknown protocol {feed} {version}')

    line_number = 0
    with Parser(str(filename), feed_def) as reader:
        with gzip.open(output_path, 'wt') as file_ptr:
            for message in reader:
                line_number += 1

                if not is_silent and line_number % 1000 == 0:
                    print(
                        f"{message['timestamp'].isoformat()} ({line_number})",
                        file=sys.stderr
                    )

                if tickers and 'symbol' in message and message['symbol'] not in tickers:
                    if not is_silent:
                        print(f"Skipping {message['symbol']}", file=sys.stderr)
                    continue

                print(json.dumps(message, cls=JSONEncoderEx), file=file_ptr)


def load_json(input_file: Path) -> Iterator[Mapping[str, Any]]:
    with gzip.open(input_file, 'rt') as file_ptr:
        for line in file_ptr:
            obj = json.loads(line, parse_float=Decimal)

            obj['timestamp'] = datetime.fromisoformat(obj['timestamp'])

            if obj['type'] == 'security_directive':
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'trading_status':
                obj['status'] = obj['status'].encode()
                obj['symbol'] = obj['symbol'].encode()
                obj['reason'] = obj['reason'].encode()
            elif obj['type'] == 'retail_liquidity_indicator':
                obj['status'] = obj['indicator'].encode()
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'operational_halt':
                obj['halt_status'] = obj['halt_status'].encode()
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'short_sale_price_test_status':
                obj['symbol'] = obj['symbol'].encode()
                obj['detail'] = obj['detail'].encode()
            elif obj['type'] == 'quote_update':
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'trade_report':
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'official_price':
                obj['price_type'] = obj['price_type'].encode()
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'trade_break':
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'auction_information':
                obj['scheduled_auction_time'] = datetime.fromisoformat(
                    obj['scheduled_auction_time'])
            elif obj['type'] == 'price_level_update':
                obj['side'] = obj['side'].encode()
                obj['symbol'] = obj['symbol'].encode()
            elif obj['type'] == 'security_event':
                obj['security_event'] = obj['security_event'].encode()
                obj['symbol'] = obj['symbol'].encode()

            yield obj


def parse_args(args):
    parser = argparse.ArgumentParser("IEX to json")
    parser.add_argument(
        '-i', '--input-file',
        help='Input filename',
        action='store',
        dest='input_filename')
    parser.add_argument(
        '-o', '--output-path',
        help='Output folder or file',
        action='store',
        dest='output_path',
        default='.')
    parser.add_argument(
        '-t', '--ticker',
        help='Add a ticker to record',
        action='append',
        dest='tickers',
        default=[])
    parser.add_argument(
        '-s', '--silent',
        help='Suppress progress report',
        action='store_true',
        dest='is_silent',
        default=False)
    parser.add_argument(
        '-v', '--verbose',
        help='Verbose',
        action='store_true',
        dest='is_verbose',
        default=False)
    return parser.parse_args(args)


def iex_to_json():
    args = parse_args(sys.argv[1:])
    if args.is_verbose:
        logging.basicConfig(level=logging.DEBUG)
    try:
        convert(
            Path(args.input_filename),
            Path(args.output_path),
            [ticker.encode() for ticker in args.tickers],
            args.is_silent
        )
        return 0
    except Exception as error:  # pylint: disable=broad-except
        print(error, file=sys.stderr)
        return -1
