from iex_parser import Parser, DEEP_1_0
import os

DEEP_SAMPLE_DATA_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20180127_20180127_IEXTP1_DEEP1.0.pcap.gz')
DEEP_DATA_FILE = os.path.join(os.environ['DATA_FOLDER'], 'data_feeds_20190503_20190503_IEXTP1_DEEP1.0.pcap.gz')

with Parser(DEEP_SAMPLE_DATA_FILE, DEEP_1_0) as reader:
    for message in reader:
        print(message)

print('Done')
