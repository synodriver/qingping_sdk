# -*- coding: utf-8 -*-
import os
import time
from unittest import IsolatedAsyncioTestCase

import dotenv

from qingping_sdk import Client

dotenv.load_dotenv("./.env")


class TestClient(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # self.client = Client(os.getenv("APP_KEY"), os.getenv("APP_SECRET"))
        pass

    async def test_get_access_token(self):
        async with Client(os.getenv("APP_KEY"), os.getenv("APP_SECRET")) as client:
            self.assertIsNotNone(client.access_token)
            self.assertIsInstance(client.access_token, str)
            device = await client.get_devices()
            print(device)
            mac = device["devices"][0]["info"]["mac"]
            print(
                await client.get_history_data(
                    mac, int(time.time()) - 3600, int(time.time())
                )
            )
            print(
                await client.get_history_events(
                    mac, int(time.time()) - 3600, int(time.time())
                )
            )
            d = await client.change_settings([mac], 60, 60)
            self.assertEqual(d, "")

            # print(await client.add_alert(mac, {
            #     "metric_name": "temperature",
            #     "operator": "lt",
            #     "threshold": 10
            # }))
            alert = await client.get_alert(mac)
            print(alert)
            #         await client.delete_alert(mac, [403499])
            #         await client.add_alert(mac, {
            #   "metric_name": "battery",
            #   "operator": "lt",
            #   "threshold": 15
            # })
            #         alert = await client.get_alert(mac)
            # print(await client.change_alert(mac, {
            #     "id": alert["alert_configs"][0]["id"],
            #     "metric_name": "temperature",
            #     "operator": "lt",
            #     "threshold": 5
            # }))
            #
            # print(await client.delete_alert(mac, [alert["alert_configs"][0]["id"]]))
            print("---groups----")
            print(await client.get_groups())
            print("---sn----")
            print(await client.get_device_info([mac], ["sn"]))


if __name__ == "__main__":
    import unittest

    unittest.main()
