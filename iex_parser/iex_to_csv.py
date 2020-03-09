"""Convert an IEX file to CSV files"""

import argparse
from datetime import datetime
from decimal import Decimal
import gzip
from pathlib import Path
import re
import sys
from typing import Any, Callable, Dict, IO, List, Mapping

from iex_parser.parser import Parser
from iex_parser.messages import DEEP_1_0, TOPS_1_6

 # data_feeds_20200305_20200305_IEXTP1_DEEP1.0.pcap.gz
FILENAME_REGEX = re.compile(r"data_feeds_(?P<start_date>\d{8})_(?P<end_date>\d{8})_(?P<protocol>[^_]+)_(?P<feed>(DEEP|TOPS))(?P<version>\d+\.\d+)\.pcap\.gz")

def int_to_str(value: int) -> str:
    return str(value)

def decimal_to_str(value: int) -> str:
    return str(value)

def bytes_to_str(value: bytes) -> str:
    return '"' + value.decode() + '"'

def timestamp_to_str(value: datetime) -> str:
    return value.isoformat()

def datetime_to_str(value: datetime) -> str:
    return value.isoformat()

FILE_FORMATS: Mapping[str, Mapping[str, Callable[[Any], str]]] = {
    'security_directive': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'flags':  int_to_str,
        'symbol': bytes_to_str,
        'round_lot_size': int_to_str,
        'adjusted_poc_close': decimal_to_str,
        'luld_tier': int_to_str
    },
    'trading_status': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'status': bytes_to_str,
        'symbol': bytes_to_str,
        'reason': bytes_to_str,
    },
    'operational_halt': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'halt_status': bytes_to_str,
        'symbol': bytes_to_str
    },
    'short_sale_price_test_status': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'status': int_to_str,
        'symbol':  bytes_to_str,
        'detail': bytes_to_str
    },
    'quote_update': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'flags': int_to_str,
        'symbol': bytes_to_str,
        'bid_size': int_to_str,
        'bid_price':  decimal_to_str,
        'ask_size': int_to_str,
        'ask_price': decimal_to_str
    },
    'trade_report': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'flags':  int_to_str,
        'symbol': bytes_to_str,
        'size': int_to_str,
        'price': decimal_to_str,
        'trade_id': int_to_str
    },
    'official_price': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'price_type': bytes_to_str,
        'symbol': bytes_to_str,
        'price': decimal_to_str
    },
    'trade_break': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'flags': int_to_str,
        'symbol':  bytes_to_str,
        'size':  int_to_str,
        'price':  decimal_to_str,
        'trade_id': int_to_str
    },
    'auction_information': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'auction_type': bytes_to_str,
        'symbol':  bytes_to_str,
        'paired_shares': int_to_str,
        'reference_price': decimal_to_str,
        'indicative_clearing_price': decimal_to_str,
        'imbalance_shares': int_to_str,
        'imbalance_side': bytes_to_str,
        'extension_number': int_to_str,
        'scheduled_auction_time': datetime_to_str,
        'auction_book_clearing_price': decimal_to_str,
        'collar_reference_price': decimal_to_str,
        'lower_auction_collar_price': decimal_to_str,
        'upper_auction_collar_price': decimal_to_str
    },
    'price_level_update': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'side': bytes_to_str,
        'flags': int_to_str,
        'symbol': bytes_to_str,
        'size': int_to_str,
        'price': decimal_to_str
    },
    'security_event' : {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'security_event': bytes_to_str,
        'symbol': bytes_to_str
    },
    'system_event': {
        'ordinal': int_to_str,
        'timestamp': timestamp_to_str,
        'event': bytes_to_str
    }
}

def convert(filename: Path, output_folder: Path, tickers: List[bytes], is_silent: bool):
    matches = FILENAME_REGEX.match(filename.name)

    if not matches:
        raise ValueError('Unable to process filename')
    
    dct = matches.groupdict()
    start_date = datetime.strptime(dct['start_date'], '%Y%m%d')
    end_date = datetime.strptime(dct['end_date'], '%Y%m%d')
    protocol = dct['protocol']
    feed = dct['feed']
    version = float(dct['version'])

    root_filename = f'data_feed_{start_date:%Y%m%d}_{end_date:%Y%m%d}_{protocol}_DEEP{version}_'
    security_directory_filename =  root_filename + 'security_directory.csv.gz'
    trading_status_filename =  root_filename + 'trading_status.csv.gz'
    operational_halt_filename =  root_filename + 'operational_halt.csv.gz'
    short_sale_price_test_status_filename =  root_filename + 'short_sale_price_test_status.csv.gz'
    security_event_filename =  root_filename + 'security_event.csv.gz'
    quote_update_filename =  root_filename + 'quote_update.csv.gz'
    price_level_update_filename =  root_filename + 'price_level_update.csv.gz'
    trade_report_filename =  root_filename + 'trade_report.csv.gz'
    official_price_filename =  root_filename + 'official_price.csv.gz'
    trade_break_filename =  root_filename + 'trade_break.csv.gz'
    auction_information_filename =  root_filename + 'auction_information.csv.gz'
    system_event_filename =  root_filename + 'system_event.csv.gz'

    feed_def = DEEP_1_0 if feed == 'DEEP' else TOPS_1_6

    file_ptr_map: Dict[str, IO[Any]] = {}
    ordinal = 0
    with Parser(str(filename), feed_def) as reader:
        with gzip.open(output_folder / security_directory_filename, "wt") as file_ptr_map['security_directive']:
            print(",".join(FILE_FORMATS['security_directive'].keys()), file=file_ptr_map['security_directive'])
            with gzip.open(output_folder / trading_status_filename, "wt") as file_ptr_map['trading_status']:
                print(",".join(FILE_FORMATS['trading_status'].keys()), file=file_ptr_map['trading_status'])
                with gzip.open(output_folder / operational_halt_filename, "wt") as file_ptr_map['operational_halt']:
                    print(",".join(FILE_FORMATS['operational_halt'].keys()), file=file_ptr_map['operational_halt'])
                    with gzip.open(output_folder / short_sale_price_test_status_filename, "wt") as file_ptr_map['short_sale_price_test_status']:
                        print(",".join(FILE_FORMATS['short_sale_price_test_status'].keys()), file=file_ptr_map['short_sale_price_test_status'])
                        with gzip.open(output_folder / quote_update_filename, "wt") as file_ptr_map['quote_update']:
                            print(",".join(FILE_FORMATS['quote_update'].keys()), file=file_ptr_map['quote_update'])
                            with gzip.open(output_folder / trade_report_filename, "wt") as file_ptr_map['trade_report']:
                                print(",".join(FILE_FORMATS['trade_report'].keys()), file=file_ptr_map['trade_report'])
                                with gzip.open(output_folder / official_price_filename, "wt") as file_ptr_map['official_price']:
                                    print(",".join(FILE_FORMATS['official_price'].keys()), file=file_ptr_map['official_price'])
                                    with gzip.open(output_folder / trade_break_filename, "wt") as file_ptr_map['trade_break']:
                                        print(",".join(FILE_FORMATS['trade_break'].keys()), file=file_ptr_map['trade_break'])
                                        with gzip.open(output_folder / auction_information_filename, "wt") as file_ptr_map['auction_information']:
                                            print(",".join(FILE_FORMATS['auction_information'].keys()), file=file_ptr_map['auction_information'])
                                            with gzip.open(output_folder / price_level_update_filename, "wt") as file_ptr_map['price_level_update']:
                                                print(",".join(FILE_FORMATS['price_level_update'].keys()), file=file_ptr_map['price_level_update'])
                                                with gzip.open(output_folder / security_event_filename, "wt") as file_ptr_map['security_event']:
                                                    print(",".join(FILE_FORMATS['security_event'].keys()), file=file_ptr_map['security_event'])
                                                    with gzip.open(output_folder / system_event_filename, "wt") as file_ptr_map['system_event']:
                                                        print(",".join(FILE_FORMATS['system_event'].keys()), file=file_ptr_map['system_event'])

                                                        for message in reader:
                                                            ordinal += 1
                                                            message['ordinal'] = ordinal

                                                            if not is_silent and ordinal % 1000 == 0:
                                                                print(f"{message['timestamp'].isoformat()} ({ordinal})", file=sys.stderr)

                                                            if tickers and 'symbol' in message and message['symbol'] not in tickers:
                                                                print(f"Skipping {message['symbol']}")
                                                                continue

                                                            file_ptr = file_ptr_map[message['type']]
                                                            formats = FILE_FORMATS[message['type']]
                                                            data = [
                                                                fmt(message[name])
                                                                for name, fmt in formats.items()
                                                            ]
                                                            print(",".join(data), file=file_ptr)

def parse_args(args):
    parser = argparse.ArgumentParser("IEX to csv")
    parser.add_argument(
        '-i', '--input-file', 
        help='Input filename',
        action='store',
        dest='input_filename')
    parser.add_argument(
        '-o', '--output-folder',
        help='Output folder',
        action='store',
        dest='output_folder',
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
    return parser.parse_args(args)

def iex_to_csv():
    args = parse_args(sys.argv[1:])
    convert(
        Path(args.input_filename),
        Path(args.output_folder),
        [ticker.encode() for ticker in args.tickers],
        args.is_silent
    )
