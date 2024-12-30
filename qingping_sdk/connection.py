# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2024 synodriver <diguohuangjiajinweijun@gmail.com>
"""
# https://qingping.feishu.cn/docs/doccnsQEUKIl4ySLumxSqYktH4d
from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from typing import Generator

import crcmod

crc16 = crcmod.mkCrcFun(0x13D65, 0xFFFF, True, 0xFFFF)


@dataclass
class Event:
    sop: bytes  # b"CG"  2 bytes
    cmd: int  # 1 bytes
    length: int  # 2 bytes
    payload: bytes  # len(payload) == length
    checksum: int  # 2 bytes

    @property
    def keys(self) -> dict:
        """解析payload字段"""
        ret = {}
        reader = BytesIO(self.payload)
        while True:
            key = reader.read(1)[0]
            length = int.from_bytes(reader.read(2), "little")
            value = reader.read(length)
            ret[key] = value
            if reader.tell() == len(self.payload):
                break
        return ret

    @keys.setter
    def keys(self, value) -> None:
        writer = BytesIO()
        for key, v in value.items():
            writer.write(key.to_bytes(1, "little"))
            writer.write(len(v).to_bytes(2, "little"))
            writer.write(v)
        self.payload = writer.getvalue()
        self.length = len(self.payload)

    def to_bytes(self) -> bytes:
        writer = BytesIO()
        writer.write(self.sop)
        writer.write(self.cmd.to_bytes(1, "little"))
        writer.write(self.length.to_bytes(2, "little"))
        writer.write(self.payload)
        # self.checksum = crc16(writer.getvalue())
        writer.write(self.checksum.to_bytes(2, "little"))  # todo 自己计算checksum
        return writer.getvalue()


def parse_history_data(data: bytes):
    time = int.from_bytes(data[:4], "little")  # 时间戳
    internal = int.from_bytes(data[4:6], "little")  # 存储间隔 单位s
    current_ptr = 6
    history = []
    while current_ptr != len(data):
        history.append(data[current_ptr : current_ptr + 6])
        current_ptr += 6
    return time, internal, history


def build_history_data(time: int, internal: int, history: list) -> bytes:
    writer = BytesIO()
    writer.write(time.to_bytes(4, "little"))
    writer.write(internal.to_bytes(2, "little"))
    for item in history:
        writer.write(item)
    return writer.getvalue()


class _State(IntEnum):
    read_first_5_bytes = 0
    read_payload = 1


class Connection:
    def __init__(self):
        self._buf = bytearray()  # type: bytearray
        self._state = _State.read_first_5_bytes
        self._tmp = None

    def feed_data(self, data: bytes) -> Generator[Event, None, None]:
        self._buf.extend(data)
        while True:
            if self._state == _State.read_first_5_bytes:
                if len(self._buf) < 5:
                    break
                sop: bytes = self._buf[:2]
                cmd: int = self._buf[2]
                length = int.from_bytes(self._buf[3:5], "little")
                self._tmp = Event(sop, cmd, length, b"", 0)
                del self._buf[:5]
                self._state = _State.read_payload
            elif self._state == _State.read_payload:
                if len(self._buf) < self._tmp.length + 2:
                    break
                payload = self._buf[: self._tmp.length]
                checksum = int.from_bytes(
                    self._buf[self._tmp.length : self._tmp.length + 2], "little"
                )
                del self._buf[: self._tmp.length + 2]
                self._state = _State.read_first_5_bytes
                self._tmp.payload = payload
                self._tmp.checksum = checksum
                ev = self._tmp
                self._tmp = None
                yield ev

    def send(self, event: Event) -> bytes:
        return event.to_bytes()
