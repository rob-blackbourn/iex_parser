# iex_parser

Parser for IEX pcap DEEP and TOPS files.

## Overview

At the time of writing the IEX exchange provides two file downloads for
historical data: DEEP and TOPS. This data is provided as a `pcap` file
which is a dump of the network activity.

This package provides an API for extracting the data from these files.

## Example

The following code processes the TOPS sample file downloaded from IEX.

```python
from iex_parser import Parser, TOPS_1_6

TOPS_SAMPLE_DATA_FILE = 'data_feeds_20180127_20180127_IEXTP1_TOPS1.6.pcap'

with Parser(TOPS_SAMPLE_DATA_FILE, TOPS_1_6) as reader:
    for message in reader:
        print(message)
```
The result looks like this:

```python
{'type': 'trading_status', 'status': b'T', 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 40, 490473, tzinfo=datetime.timezone.utc), 'symbol': b'SPEM', 'reason': b''}
{'type': 'trading_status', 'status': b'H', 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 42, 95642, tzinfo=datetime.timezone.utc), 'symbol': b'INCO', 'reason': b'NA'}
{'type': 'trading_status', 'status': b'H', 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 42, 852349, tzinfo=datetime.timezone.utc), 'symbol': b'CHSCN', 'reason': b'NA'}
{'type': 'price_level_update', 'side': b'S', 'flags': 1, 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 44, 856983, tzinfo=datetime.timezone.utc), 'symbol': b'ATLO', 'size': 8755, 'price': Decimal('38.95')}
{'type': 'price_level_update', 'side': b'S', 'flags': 0, 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 44, 856983, tzinfo=datetime.timezone.utc), 'symbol': b'ATLO', 'size': 37222, 'price': Decimal('48')}
{'type': 'price_level_update', 'side': b'S', 'flags': 1, 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 44, 856987, tzinfo=datetime.timezone.utc), 'symbol': b'ATLO', 'size': 8958, 'price': Decimal('38.95')}
{'type': 'price_level_update', 'side': b'S', 'flags': 0, 'timestamp': datetime.datetime(2018, 1, 27, 15, 23, 44, 856987, tzinfo=datetime.timezone.utc), 'symbol': b'ATLO', 'size': 37019, 'price': Decimal('48')}
```

The following code processes the DEEP sample file downloaded from IEX.

```python
from iex_parser import Parser, DEEP_1_0

DEEP_SAMPLE_DATA_FILE = 'data_feeds_20180127_20180127_IEXTP1_DEEP1.0.pcap'

with Parser(DEEP_SAMPLE_DATA_FILE, DEEP_1_0) as reader:
    for message in reader:
        print(message)
```