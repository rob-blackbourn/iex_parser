from typing import Mapping, List

SYSTEM_EVENT_TYPES: Mapping[bytes, str] = {
    b'O': "start_of_messages",
    b'S': "start_of_system_hours",
    b'R': "start_of_regular_hours",
    b'C': "end_of_messages",
    b'E': "end_of_system_hours",
    b'M': "end_of_regular_hours",
}

LULD_TIER = {
    0x00: 'not_applicable',
    0x01: 'tier_1_nms_stock',
    0x02: 'tier_2_nms_stock'
}


def from_security_directory_flags(flags: int) -> List[str]:
    flag_set = []
    if flags & 0x80 != 0:
        flag_set.append('test')
    if flags & 0x40 != 0:
        flag_set.append('when_issued')
    if flags & 0x20 != 0:
        flag_set.append('etp')
    return flag_set


TRADING_STATUS_MESSAGES = {
    b"H": 'all_halted',
    b"O": "iex_released",
    b"P": "iex_paused",
    b"T": "iex_trading",
}


def from_sale_condition_flags(flags: int) -> List[str]:
    flag_set = []
    if flags & 0x80 != 0:
        flag_set.append('iso')
    if flags & 0x40 != 0:
        flag_set.append('extended_hours')
    if flags & 0x20 != 0:
        flag_set.append('odd_lot')
    if flags & 0x10 != 0:
        flag_set.append('trade_through_excempt')
    if flags & 0x08 != 0:
        flag_set.append('single_price_cross')
    return flag_set


def is_last_sale_eligable(flags: int) -> bool:
    return flags & 0x40 == 0 and flags & 0x20 == 0


def is_high_low_price_eligable(flags: int) -> bool:
    return flags & 0x40 == 0 and flags & 0x20 == 0


def is_volume_eligable(flags: int) -> bool:
    return True


OFFICIAL_PRICE_TYPE = {
    b'Q': 'open',
    b'M': 'close'
}

SECURITY_EVENT = {
    b'O': 'opening',
    b'C': 'closing'
}
