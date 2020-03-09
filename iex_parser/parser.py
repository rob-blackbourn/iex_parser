import logging
import queue
from scapy.all import PcapReader, Packet
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP
import struct
import threading
from typing import NamedTuple, Mapping, Optional, List, Any
from .messages import decode_message

logger = logging.getLogger(__name__)


class Header(NamedTuple):
    """
    Version                        0 1 Byte      1 (0x1) Version of Transport specification
    (Reserved)                     1 1           Reserved byte
    Message Protocol ID            2 2 Short     Unique identifier of the higher-layer protocol
    Channel ID                     4 4 Integer   Identifies the stream of bytes/sequenced messages
    Session ID                     8 4 Integer   Identifies the session
    Payload Length                12 2 Short     Byte length of the payload
    Message Count                 14 2 Short     Number of messages in the payload
    Stream Offset                 16 8 Long      Byte offset of the data stream
    First Message Sequence Number 24 8 Long      Sequence of the first message in the segment
    Send Time                     32 8 Timestamp Send time of segment
    """
    version: int
    message_protocol_id: int
    channel_id: int
    session_id: int
    payload_length: int
    message_count: int
    stream_offset: int
    first_message_seq_number: int
    send_time: int


class DeepPcapReader:

    def __init__(self, reader: PcapReader, protocol: str, queue_length) -> None:
        self.reader = reader
        self.protocol = protocol
        self.messages = queue.Queue(queue_length)
        self.sentinal = object()
        self.cancellation_token = threading.Event()
        self.fill_thread = threading.Thread(target=self._fill)


    def __iter__(self):
        self.fill_thread.start()
        return self


    def __next__(self) -> Mapping[str, Any]:
        message = self.messages.get()
        if message == self.sentinal:
            self.fill_thread.join()
            raise StopIteration
        return message


    def _fill(self) -> None:
        is_eof = False

        while not (is_eof or self.cancellation_token.is_set()):
            logging.debug(f'Reading packet: len(queue)={self.messages.qsize()}')
            packet: Packet = self.reader.read_packet()
            if packet is None:
                is_eof = True
                self.messages.put(self.sentinal)
            elif not isinstance(packet, Ether) and packet.haslayer(UDP):
                raise RuntimeError('Invalid packet')
            else:
                layer: UDP = packet[UDP]
                buf = layer.payload.load
                messages = self._read(buf)
                if messages is not None:
                    for message in messages:
                        self.messages.put(message)

        logging.debug('All packets read')


    HEADER_PATTERN = '<BxHIIHHqqq'
    HEADER_SIZE = struct.calcsize(HEADER_PATTERN)
    MESSAGE_LENGTH_PATTERN = '<h'
    MESSAGE_LENGTH_SIZE = struct.calcsize(MESSAGE_LENGTH_PATTERN)


    def _read(self, buf: bytes) -> Optional[List[Mapping[str, Any]]]:
        # Read the header.
        header = Header(*struct.unpack(self.HEADER_PATTERN, buf[:self.HEADER_SIZE]))
        if len(buf) != self.HEADER_SIZE + header.payload_length:
            raise RuntimeError('Invalid payload')
        if header.payload_length == 0:
            return None

        # Read the messages.
        messages = []
        start = self.HEADER_SIZE
        for message_number in range(header.message_count):
            end = start + self.MESSAGE_LENGTH_SIZE
            message_lengh = struct.unpack("<H", buf[start:end])[0]
            start = end
            end += message_lengh
            message = self._parse_message(buf[start:end])
            messages.append(message)
            start = end

        return messages


    def _parse_message(self, buf: bytes) -> Mapping[str, Any]:
        message_type = buf[0]
        message_body = buf[1:]
        return decode_message(self.protocol, message_type, message_body)


class Parser:

    # noinspection PyArgumentList
    def __init__(self, filename: str, protocol: str, queue_length=25000) -> None:
        self.reader = PcapReader(filename)
        self.protocol = protocol
        self.queue_length = queue_length


    def __enter__(self) -> DeepPcapReader:
        self.reader.__enter__()
        return DeepPcapReader(self.reader, self.protocol, self.queue_length)


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.reader.__exit__(exc_type, exc_val, exc_tb)
