"""Load an IEX file that has been converted to JSON"""

from pathlib import Path

from iex_parser.iex_to_json import load_json

INPUT_FILENAME = Path('data_feed_20180127_20180127_IEXTP1_DEEP1.0.json.gz')

for obj in load_json(INPUT_FILENAME):
    if obj['type'] == 'trade_report':
        print(obj)
