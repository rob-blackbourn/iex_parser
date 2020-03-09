# iex_parser

Parser for IEX pcap DEEP and TOPS files.

## Overview

At the time of writing the IEX exchange provides two file downloads for
historical data: DEEP and TOPS. This data is provided as a `pcap` file
which is a dump of the network activity.

This package provides an API for extracting the data from these files.

## Installation

Install from PyPi.

```bash
pip install iex_parser
```

## Example

The following code processes the TOPS sample file downloaded from IEX. Note the file doesn't have to be unzipped.

```python
from iex_parser import Parser, TOPS_1_6

TOPS_SAMPLE_DATA_FILE = 'data_feeds_20180127_20180127_IEXTP1_TOPS1.6.pcap.gz'

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

DEEP_SAMPLE_DATA_FILE = 'data_feeds_20180127_20180127_IEXTP1_DEEP1.0.pcap.gz'

with Parser(DEEP_SAMPLE_DATA_FILE, DEEP_1_0) as reader:
    for message in reader:
        print(message)
```

## Messages

The messages are returned as dictionaries.

### Security Directive

```python
{
    'type': 'security_directive',
    'flags': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'round_lot_size': int,
    'adjusted_poc_close': decimal.Decimal,
    'luld_tier': int
}
```

### Trading Status

```python
{
    'type': 'trading_status',
    'status': bytes,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'reason': bytes
}
```

### Operational Halt

```python
{
    'type': 'operational_halt',
    'halt_status': bytes,
    'timestamp': datetime.datetime,
    'symbol': bytes
}
```

### Short Sale Price Test Status

```python
{
    'type': 'short_sale_price_test_status',
    'status': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'detail': bytes
}
```

### Quote Update

```python
{
    'type': 'quote_update',
    'flags': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'bid_size': int,
    'bid_price': decimal.Decimal,
    'ask_size': int,
    'ask_price': decimal.Decimal
}
```

### Trade Report

```python
{
    'type': 'trade_report',
    'flags': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'size': int,
    'price': decimal.Decimal,
    'trade_id': int
}
```

### Official Price

```python
{
    'type': 'official_price',
    'price_type': bytes,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'price': deccimal.Decimal
}
```

### Trade Break

```python
{
    'type': 'trade_break',
    'flags': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'size': int,
    'price': decimal.Decimal,
    'trade_id': int
}
```

### Auction Information

```python
{
    'type': 'auction_information',
    'auction_type': bytes,
    'timestamp': decimal.Decimal,
    'symbol': bytes,
    'paired_shares': int,
    'reference_price': decimal.Decmal,
    'indicative_clearing_price': decimal.Decimal,
    'imbalance_shares': int,
    'imbalance_side': bytes,
    'extension_number': int,
    'scheduled_auction_time': datetime.datetime,
    'auction_book_clearing_price': decimal.Decimal,
    'collar_reference_price': decimal.Decimal,
    'lower_auction_collar_price': decimal.Decimal,
    'upper_auction_collar_price': decimal.Decimal
}
```

### Price Level Update

```python
{
    'type': 'price_level_update',
    'side': bytes,
    'flags': int,
    'timestamp': datetime.datetime,
    'symbol': bytes,
    'size': int,
    'price': decimal.Decimal
}
```

### Secrity Event

```python
{
    'type': 'security_event',
    'security_event': bytes,
    'timestamp': datetime.datetime,
    'symbol': bytes
}
```

## Notes

Becuase the data is distributed as a dump of network packets, there are a lot of "empty" 
packets. These take time to read and slow the delivery of the real data. To handle this
the packets are read on a separate python thread and queued. The size of the queue is an
optional parameter to the `Parser`, and has been set by experimentation to 25000.
 
## Command line tool

There is a command line tool that takes a downloaded file and converts it
to csv files.

### Usage

```bash
$ iex-to-csv -i <input-file> -o <output-folder> [-s] [-t <ticker> ...]
```

The input file must be as downloaded from IEX. This `-s` flag can be used to
suppress the progress printing. The `-t` flag can be used to select specific
tickers.

For example:

```bash
$ iex-to-csv -i ~/data/raw/data_feeds_20200305_20200305_IEXTP1_DEEP1.0.pcap.gz -o ~/data/csv
```
