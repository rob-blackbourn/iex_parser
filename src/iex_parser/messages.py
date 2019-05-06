from datetime import datetime, timezone
from decimal import Decimal
import struct
from typing import Mapping, Any, Callable, List


def _from_timestamp(value: int) -> datetime:
    return datetime.fromtimestamp(value / 10 ** 9, tz=timezone.utc)


def _to_str(value: bytes) -> str:
    return value.decode('utf-8').strip()


def _from_price(value: int) -> Decimal:
    return Decimal(value) / 10 ** 4


SYSTEM_EVENT_TYPES = {
    79: "start_of_messages",
    83: "start_of_system_hours",
    82: "start_of_regular_hours",
    67: "end_of_messages",
    69: "end_of_system_hours",
    77: "end_of_regular_hours",
}


def _decode_system_event(buf: bytes) -> Mapping[str, Any]:
    (system_event, timestamp) = struct.unpack('<Bq', buf)
    return {
        'type': 'system_event',
        'event': SYSTEM_EVENT_TYPES[system_event],
        'timestamp': _from_timestamp(timestamp)
    }


LULD_TIER = {
    0x00: 'not_applicable',
    0x01: 'tier_1_nms_stock',
    0x02: 'tier_2_nms_stock'
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

    flag_set = []
    if flags & 0x80 != 0:
        flag_set.append('test')
    if flags & 0x40 != 0:
        flag_set.append('when_issued')
    if flags & 0x20 != 0:
        flag_set.append('etp')

    return {
        'type': 'security_directive',
        'flags': flag_set,
        'timestamp': _from_timestamp(timestamp),
        'round_lot_size': round_lot_size,
        'adjusted_poc_close': _from_price(adjusted_poc_close),
        'luld_tier': LULD_TIER[luld_tier]
    }


TRADING_STATUS_MESSAGES = {
    b"H": 'all_halted',
    b"O": "iex_released",
    b"P": "iex_paused",
    b"T": "iex_trading",
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
        'status': _to_str(status),
        'description': TRADING_STATUS_MESSAGES[status],
        'reason': _to_str(reason)
    }


def _decode_operational_halt(buf: bytes) -> Mapping[str, Any]:
    (
        halt_status,
        timestamp,
        symbol
    ) = struct.unpack('<1sq8s', buf)
    return {
        'type': 'operational_halt',
        'halt_status': _to_str(halt_status),
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol)
    }


def _decode_short_sale_price_test_status(buf: bytes) -> Mapping[str, Any]:
    (
        short_sale_status,
        timestamp,
        symbol,
        detail
    ) = struct.unpack('<Bq8s1s', buf)
    return {
        'type': 'short_sale_price_test_status',
        'is_test': short_sale_status == 0x01,
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol),
        'detail': _to_str(detail)
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
        'symbol': _to_str(symbol),
        'bid_size': bid_size,
        'bid_price': _from_price(bid_price),
        'ask_size': ask_size,
        'ask_price': _from_price(ask_price)
    }


def _from_sale_condition_flags(flags: int) -> List[str]:
    flag_set = []
    if flags & 0x80 != 0:
        flag_set.append('iso')
    if flags & 0x40 != 0:
        flag_set.append('out_of_hours')
    if flags & 0x20 != 0:
        flag_set.append('odd_lot')
    if flags & 0x10 != 0:
        flag_set.append('trade_through_except')
    if flags & 0x08 != 0:
        flag_set.append('single_price_cross')
    return flag_set


def _decode_trade_report(buf: bytes) -> Mapping[str, Any]:
    (
        flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id
    ) = struct.unpack('<Bq8sLqq', buf)

    flag_set = _from_sale_condition_flags(flags)

    return {
        'type': 'trade_report',
        'flags': flag_set,
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol),
        'size': size,
        'price': _from_price(price),
        'trade_id': trade_id
    }


PRICE_TYPE = {
    b'Q': 'open',
    b'M': 'close'
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
        'price_type': PRICE_TYPE.get(price_type, _to_str(price_type)),
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol),
        'price': _from_price(price)
    }


def _decode_trade_break(buf: bytes) -> Mapping[str, Any]:
    (
        sale_flags,
        timestamp,
        symbol,
        size,
        price,
        trade_id,
    ) = struct.unpack('<1sq8sLqq', buf)

    flag_set = _from_sale_condition_flags(sale_flags)

    return {
        'type': 'trade_break',
        'sale_flags': flag_set,
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol),
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
        'auction_type': _to_str(auction_type),
        'timestamp': _from_price(timestamp),
        'symbol': _to_str(symbol),
        'paired_shares': paired_shares,
        'reference_price': _from_price(reference_price),
        'indicative_clearing_price': _from_price(indicative_clearing_price),
        'imbalance_shares': imbalance_shares,
        'imbalance_side': _to_str(imbalance_side),
        'extension_number': extension_number,
        'scheduled_auction_time': scheduled_auction_time,
        'auction_book_clearing_price': _from_price(auction_book_clearing_price),
        'collar_reference_price': _from_price(collar_reference_price),
        'lower_auction_collar_price': _from_price(lower_auction_collar_price),
        'upper_auction_collar_price': _from_price(upper_auction_collar_price)
    }


def _decode_price_level_update(side: str, buf: bytes) -> Mapping[str, Any]:
    (
        event_flags,
        timestamp,
        symbol,
        size,
        price
    ) = struct.unpack('<Bq8sIq', buf)
    return {
        'type': 'price_level_update',
        'side': side,
        'event_flags': 'complete' if event_flags == 1 else 'processing',
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol),
        'size': size,
        'price': _from_price(price)
    }


SECURITY_EVENT = {
    b'O': 'opening',
    b'C': 'closing'
}


def _decode_security_event_message(buf: bytes) -> Mapping[str, Any]:
    (
        security_event,
        timestamp,
        symbol
    ) = struct.unpack('<1sq8s', buf)

    return {
        'type': 'security_event',
        'security_event': SECURITY_EVENT.get(security_event, _to_str(security_event)),
        'timestamp': _from_timestamp(timestamp),
        'symbol': _to_str(symbol)
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
    0x38: lambda buf: _decode_price_level_update('buy', buf),
    0x35: lambda buf: _decode_price_level_update('sell', buf),
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
