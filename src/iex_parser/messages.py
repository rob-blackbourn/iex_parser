from datetime import datetime, timezone
from decimal import Decimal
import struct
from typing import Mapping, Any, Callable


def _from_timestamp(value: int) -> datetime:
    return datetime.fromtimestamp(value / 10 ** 9, tz=timezone.utc)


def _from_event_time(value: int) -> datetime:
    return datetime.fromtimestamp(value, tz=timezone.utc)


def _from_price(value: int) -> Decimal:
    return Decimal(value) / 10 ** 4


def _decode_system_event(buf: bytes) -> Mapping[str, Any]:
    (
        system_event,
        timestamp
    ) = struct.unpack('<1sq', buf)

    return {
        'type': 'system_event',
        'event': system_event.strip(),
        'timestamp': _from_timestamp(timestamp)
    }


def _decode_security_directory(buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        round_lot_size,
        adjusted_poc_close,
        luld_tier
    ) = struct.unpack('<Bq8sLqB', buf)

    return {
        'type': 'security_directive',
        'flags': flags,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'round_lot_size': round_lot_size,
        'adjusted_poc_close': adjusted_poc_close,
        'luld_tier': luld_tier
    }


def _decode_trading_status(buf: bytes) -> Mapping[str, Any]:
    (
        status,
        timestamp,
        symbol,
        reason
    ) = struct.unpack('<1sq8s4s', buf)

    return {
        'type': 'trading_status',
        'status': status.strip(),
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'reason': reason.strip()
    }


def _decode_operational_halt(buf: bytes) -> Mapping[str, Any]:
    (
        halt_status,
        timestamp,
        symbol
    ) = struct.unpack('<1sq8s', buf)

    return {
        'type': 'operational_halt',
        'halt_status': halt_status.strip(),
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip()
    }


def _decode_short_sale_price_test_status(buf: bytes) -> Mapping[str, Any]:
    (
        status,
        timestamp,
        symbol,
        detail
    ) = struct.unpack('<Bq8s1s', buf)

    return {
        'type': 'short_sale_price_test_status',
        'status': status,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'detail': detail.strip()
    }


def _decode_quote_update(buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        bid_size,
        bid_price,
        ask_price,
        ask_size
    ) = struct.unpack('<Bq8sLqqL', buf)

    return {
        'type': 'quote_update',
        'flags': flags,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'bid_size': bid_size,
        'bid_price': _from_price(bid_price),
        'ask_size': ask_size,
        'ask_price': _from_price(ask_price)
    }


def _decode_trade_report(buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id
    ) = struct.unpack('<Bq8sLqq', buf)

    return {
        'type': 'trade_report',
        'flags': flags,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'size': size,
        'price': _from_price(price),
        'trade_id': trade_id
    }


def _decode_official_price(buf: bytes) -> Mapping[str, Any]:
    (
        price_type,
        timestamp,
        symbol,
        price
    ) = struct.unpack('<1sq8sq', buf)

    return {
        'type': 'official_price',
        'price_type': price_type.strip(),
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'price': _from_price(price)
    }


def _decode_trade_break(buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id,
    ) = struct.unpack('<1sq8sLqq', buf)

    return {
        'type': 'trade_break',
        'flags': flags,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'size': size,
        'price': _from_price(price),
        'trade_id': trade_id
    }


def _decode_auction_information(buf: bytes) -> Mapping[str, Any]:
    (
        auction_type,
        timestamp,
        symbol,
        paired_shares,
        reference_price,
        indicative_clearing_price,
        imbalance_shares,
        imbalance_side,
        extension_number,
        scheduled_auction_time,
        auction_book_clearing_price,
        collar_reference_price,
        lower_auction_collar_price,
        upper_auction_collar_price
    ) = struct.unpack('<1sq8sLqqL1sBLqqqq', buf)

    return {
        'type': 'auction_information',
        'auction_type': auction_type.strip(),
        'timestamp': _from_price(timestamp),
        'symbol': symbol.strip(),
        'paired_shares': paired_shares,
        'reference_price': _from_price(reference_price),
        'indicative_clearing_price': _from_price(indicative_clearing_price),
        'imbalance_shares': imbalance_shares,
        'imbalance_side': imbalance_side.strip(),
        'extension_number': extension_number,
        'scheduled_auction_time': _from_event_time(scheduled_auction_time),
        'auction_book_clearing_price': _from_price(auction_book_clearing_price),
        'collar_reference_price': _from_price(collar_reference_price),
        'lower_auction_collar_price': _from_price(lower_auction_collar_price),
        'upper_auction_collar_price': _from_price(upper_auction_collar_price)
    }


def _decode_price_level_update(side: bytes, buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        size,
        price
    ) = struct.unpack('<Bq8sIq', buf)

    return {
        'type': 'price_level_update',
        'side': side,
        'flags': flags,
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip(),
        'size': size,
        'price': _from_price(price)
    }


def _decode_security_event_message(buf: bytes) -> Mapping[str, Any]:
    (
        event,
        timestamp,
        symbol
    ) = struct.unpack('<1sq8s', buf)

    return {
        'type': 'security_event',
        'security_event': event.strip(),
        'timestamp': _from_timestamp(timestamp),
        'symbol': symbol.strip()
    }


_DECODERS: Mapping[int, Callable[[bytes], Mapping[str, Any]]] = {
    0x53: _decode_system_event,
    0x44: _decode_security_directory,
    0x48: _decode_trading_status,
    0x4f: _decode_operational_halt,
    0x50: _decode_short_sale_price_test_status,
    0x51: _decode_quote_update,
    0x54: _decode_trade_report,
    0x58: _decode_official_price,
    0x42: _decode_trade_break,
    0x41: _decode_auction_information,
    0x38: lambda buf: _decode_price_level_update(b'B', buf),
    0x35: lambda buf: _decode_price_level_update(b'S', buf),
    0x45: _decode_security_event_message
}

DEEP_1_0 = 'DEEPv1.0'
TOPS_1_6 = 'TOPSv1.6'

_VERSIONED_DECODERS: Mapping[str, Mapping[int, Callable[[bytes], Mapping[str, Any]]]] = {
    DEEP_1_0: _DECODERS,
    TOPS_1_6: _DECODERS
}


def decode_message(version: str, message_type: int, buf: bytes) -> Mapping[str, Any]:
    return _VERSIONED_DECODERS[version][message_type](buf)
