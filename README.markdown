<h1 align="center"><i>✨ qingping_sdk ✨ </i></h1>


[![pypi](https://img.shields.io/pypi/v/qingping_sdk.svg)](https://pypi.org/project/qingping_sdk/)
![python](https://img.shields.io/pypi/pyversions/qingping_sdk)
![implementation](https://img.shields.io/pypi/implementation/qingping_sdk)
![wheel](https://img.shields.io/pypi/wheel/qingping_sdk)
![license](https://img.shields.io/github/license/synodriver/qingping_sdk.svg)
![action](https://img.shields.io/github/actions/workflow/status/synodriver/qingping_sdk/upload.yaml?branch=main)

# Usage 
```python
import os
import time
from qingping_sdk import Client

async def main():
    async with Client(os.getenv("APP_KEY"), os.getenv("APP_SECRET")) as client:
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
        d = await client.change_settings(
            [mac], 60, 60
        )
        alert = await client.get_alert(mac)
        print(alert)
        print(await client.delete_alert(mac, [alert["alert_configs"][0]["id"]]))
        print("---groups----")
        print(await client.get_groups())
        print("---sn----")
        print(await client.get_device_info([mac], ["sn"]))

asyncio.run(main())
```

# Public functions
```python
class Client:

    def __init__(self, app_key: str, app_secret: str, endpoint: str = None, api_endpoint: str = None, client_session: Incomplete | None = None, close_on_exit: bool = True, loop: asyncio.AbstractEventLoop = None, **kw) -> None: ...
    async def aclose(self) -> None: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
    async def send_request(self, method: str = 'GET', url: str = None, params: dict = None, json: dict = None): ...
    async def bind_device(self, device_token: str, product_id: int, timestamp: int = None) -> Device: ...
    async def delete_device(self, mac: list[str], timestamp: int = None): ...
    async def get_devices(self, group_id: int = None, offset: int = None, limit: int = None, role: str = None, timestamp: int = None) -> DeviceResponse: ...
    async def get_history_data(self, mac: str, start_time: int, end_time: int, timestamp: int = None, offset: int = None, limit: int = None) -> HistoryDataResponse: ...
    async def get_history_events(self, mac: str, start_time: int, end_time: int, timestamp: int = None, offset: int = None, limit: int = None) -> HistoryEventResponse: ...
    async def change_settings(self, mac: list[str], report_interval: int, collect_interval: int, timestamp: int = None): ...
    async def add_alert(self, mac: str, alert_config: AlertConfig, timestamp: int = None): ...
    async def get_alert(self, mac: str, timestamp: int = None) -> GetAlertResponse: ...
    async def change_alert(self, mac: str, alert_config: AlertConfig, timestamp: int = None): ...
    async def delete_alert(self, mac: str, config_id: list[int], timestamp: int = None): ...
    async def get_groups(self, timestamp: int = None) -> GetGroupsResponse: ...
    async def get_device_info(self, mac_list: list[str], profile: list[str], timestamp: int = None) -> DeviceInfoResponse: ...


@dataclass
class Event:
    sop: bytes
    cmd: int
    length: int
    payload: bytes
    checksum: int
    @property
    def keys(self) -> dict: ...
    @keys.setter
    def keys(self, value) -> None: ...
    def to_bytes(self) -> bytes: ...
    def __init__(self, sop, cmd, length, payload, checksum) -> None: ...

def parse_history_data(data: bytes): ...
def build_history_data(time: int, internal: int, history: list) -> bytes: ...

class Connection:
    def __init__(self) -> None: ...
    def feed_data(self, data: bytes) -> Generator[Event, None, None]: ...
    def send(self, event: Event) -> bytes: ...

```
