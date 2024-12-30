# -*- coding: utf-8 -*-
from unittest import TestCase

from qingping_sdk import Connection, Event, build_history_data, parse_history_data

data = bytes.fromhex(
    "43 47 31 1F 01 01 10 00 A9 F4 9F 95 FF 08 B48B 9C AB 35 8F D3 49 46 E5 02 10 00 45 30 33 30 31 35 44 37 34 39 44 45 36 32 36 35 03 F6 00 B6 88 77 5C 05 00 9A C2 2F 66 27 4E 9A C2 2F 67 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 65 27 4E 9A C2 2F 66 27 4E 9A C2 2F 66 27 4E D3 70".strip()
)
data2 = bytes.fromhex("")


class TestCon(TestCase):
    def setUp(self):
        self.con = Connection()

    def test_feed(self):
        for ev in self.con.feed_data(data):
            print(ev)
            self.assertEqual(ev.length, len(ev.payload))
            print(ev.keys)
            ev.keys = ev.keys
            his = parse_history_data(ev.keys[3])
            self.assertEqual(build_history_data(*his), ev.keys[3])

            self.assertEqual(ev.to_bytes(), data)
