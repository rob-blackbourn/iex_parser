from datetime import datetime
from decimal import Decimal
from iex_parser import Parser, DEEP_1_0
import gzip
import json
import os


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj.to_integral == obj else float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        else:
            return super().default(obj)


DEEP_SAMPLE_DATA_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20180127_20180127_IEXTP1_DEEP1.0.pcap.gz')
DEEP_DATA_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20190503_20190503_IEXTP1_DEEP1.0.pcap.gz')

DEEP_SAMPLE_JSON_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20180127_20180127_IEXTP1_DEEP1.0.json.gz')
DEEP_JSON_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20190503_20190503_IEXTP1_DEEP1.0.json.gz')

with gzip.open(DEEP_JSON_FILE, "wt") as writer:
    with Parser(DEEP_DATA_FILE, DEEP_1_0) as reader:
        for message in reader:
            text = json.dumps(message, cls=JsonEncoder)
            print(text, file=writer)

print('Done')
