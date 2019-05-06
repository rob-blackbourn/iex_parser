from iex_parser import Parser, DEEP_1_0, TOPS_1_6

DEEP_DATA_FILE = '/home/rtb/Data/iextrading.com/data_feeds_20190503_20190503_IEXTP1_DEEP1.0.pcap'
DEEP_SAMPLE_DATA_FILE = '/home/rtb/Data/iextrading.com/data_feeds_20180127_20180127_IEXTP1_DEEP1.0.pcap'
TOPS_SAMPLE_DATA_FILE = '/home/rtb/Data/iextrading.com/data_feeds_20180127_20180127_IEXTP1_TOPS1.6.pcap'

with Parser(TOPS_SAMPLE_DATA_FILE, TOPS_1_6) as reader:
    for message in reader:
        print(message)

print('Done')
