# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2024 synodriver <diguohuangjiajinweijun@gmail.com>
"""
# https://developer.qingping.co/cloud-to-cloud/open-apis
import asyncio
import json
import time
from typing import List

import aiohttp

from qingping_sdk.exceptions import (
    AuthException,
    ConflictException,
    ExpiredException,
    NotFoundException,
    RequestException,
    ServerException,
)
from qingping_sdk.typing import (
    AlertConfig,
    Device,
    DeviceInfoResponse,
    DeviceResponse,
    GetAccessTokenResponse,
    GetAlertResponse,
    GetGroupsResponse,
    HistoryDataResponse,
    HistoryEventResponse,
)
from qingping_sdk.utils import create_auth

JSON_ENCODING = "utf-8"
DEFAULT_JSON_DECODER = json.loads
DEFAULT_JSON_ENCODER = json.dumps
DEFAULT_ENDPOINT = "oauth.cleargrass.com"
DEFAULT_API_ENDPOINT = "apis.cleargrass.com"


class Client:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        endpoint: str = None,
        api_endpoint: str = None,
        client_session=None,
        close_on_exit: bool = True,
        loop: asyncio.AbstractEventLoop = None,
        **kw,
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self._endpoint = endpoint or DEFAULT_ENDPOINT
        self._api_endpoint = api_endpoint or DEFAULT_API_ENDPOINT

        self.kw = kw
        self.loads = (
            self.kw.pop("loads") if "loads" in self.kw else DEFAULT_JSON_DECODER
        )  # json serialize
        self.dumps = (
            self.kw.pop("dumps") if "dumps" in self.kw else DEFAULT_JSON_ENCODER
        )
        self._loop = loop or asyncio.get_running_loop()
        self.client_session = client_session or aiohttp.ClientSession(
            json_serialize=self.dumps
        )  # aiohttp的会话
        self._close_on_exit = close_on_exit

        self._task = None
        self._ready = self._loop.create_future()
        self.access_token = None

    async def _get_access_token(self) -> GetAccessTokenResponse:
        auth_str = create_auth(self.app_key, self.app_secret)
        async with self.client_session.post(
            f"https://{self._endpoint}/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_str}",
            },
            data={
                "grant_type": "client_credentials",
                "scope": "device_full_access",
            },
        ) as resp:
            if resp.status != 200:
                raise AuthException(await resp.text())
            return await resp.json(loads=self.loads)

    async def aclose(self):
        await self.client_session.close()

    async def __aenter__(self):
        self._task = self._loop.create_task(self._refresh_token())
        await self._ready
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        if self._close_on_exit:
            await self.aclose()
        return False

    async def _refresh_token(self):
        while True:
            access_token_data = await self._get_access_token()
            self.access_token = access_token_data["access_token"]
            if not self._ready.done() and not self._ready.cancelled():
                self._ready.set_result(None)
            await asyncio.sleep(access_token_data["expires_in"])
        # def cb():
        #     self._loop.create_task(self._refresh_token())
        #
        # self._handle = self._loop.call_later(access_token_data["expires_in"], cb)

    async def send_request(
        self, method="GET", url: str = None, params: dict = None, json: dict = None
    ):
        url = url or f"https://{self._api_endpoint}/v1/apis/devices"
        async with self.client_session.request(
            method,
            url,
            params=params,
            json=json,
            headers={"Authorization": f"Bearer {self.access_token}"},
        ) as resp:
            if resp.status == 200:
                try:
                    return await resp.json(loads=self.loads)
                except aiohttp.client_exceptions.ContentTypeError:
                    return await resp.text()
            elif resp.status == 400:
                raise RequestException(await resp.text())
            elif resp.status in (401, 403):
                raise AuthException(await resp.text())
            elif resp.status == 404:
                raise NotFoundException(await resp.text())
            elif resp.status == 408:
                raise ExpiredException(await resp.text())
            elif resp.status == 409:
                raise ConflictException(await resp.text())
            elif resp.status in (500, 503):
                raise ServerException(await resp.text())

    async def bind_device(
        self, device_token: str, product_id: int, timestamp: int = None
    ) -> Device:
        """
        绑定设备
        :param device_token:
        :param product_id:https://developer.qingping.co/cloud-to-cloud/specification-guidelines#21-%E4%BA%A7%E5%93%81%E5%88%97%E8%A1%A8
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        timestamp = timestamp or int(time.time() * 1000)
        return await self.send_request(
            "POST",
            f"https://{self._api_endpoint}/v1/apis/devices",
            json={
                "device_token": device_token,
                "product_id": product_id,
                "timestamp": timestamp,
            },
        )

    async def delete_device(self, mac: List[str], timestamp: int = None):
        timestamp = timestamp or int(time.time() * 1000)
        return await self.send_request(
            "DELETE",
            f"https://{self._api_endpoint}/v1/apis/devices",
            json={"mac": mac, "timestamp": timestamp},
        )

    async def get_devices(
        self,
        group_id: int = None,
        offset: int = None,
        limit: int = None,
        role: str = None,
        timestamp: int = None,
    ) -> DeviceResponse:
        """
        设备列表
        :param group_id:
        :param offset:
        :param limit:
        :param role: 请求者角色（只有是代理商角色需要填写这个字段，代理商标识："agent"）
        :return:
        """
        params = {"timestamp": timestamp or int(time.time() * 1000)}
        if group_id is not None:
            params["group_id"] = group_id
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if role is not None:
            params["role"] = role
        return await self.send_request(
            "GET", f"https://{self._api_endpoint}/v1/apis/devices", params=params
        )

    async def get_history_data(
        self,
        mac: str,
        start_time: int,
        end_time: int,
        timestamp: int = None,
        offset: int = None,
        limit: int = None,
    ) -> HistoryDataResponse:
        """
        设备历史数据
        :param mac: 设备mac地址
        :param start_time: 开始时间戳 单位s
        :param end_time: 结束时间戳
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :param offset: 偏移量
        :param limit: 最大返回数量 不得超过200条
        :return:
        """
        params = {
            "mac": mac,
            "start_time": start_time,
            "end_time": end_time,
            "timestamp": timestamp or int(time.time() * 1000),
        }
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        return await self.send_request(
            "GET",
            f"https://{self._api_endpoint}/v1/apis/devices/data",
            params=params,
        )

    async def get_history_events(
        self,
        mac: str,
        start_time: int,
        end_time: int,
        timestamp: int = None,
        offset: int = None,
        limit: int = None,
    ) -> HistoryEventResponse:
        """
        设备历史事件
        :param mac: 设备mac地址
        :param start_time: 开始时间戳 单位s
        :param end_time: 结束时间戳
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :param offset: 偏移量
        :param limit: 最大返回数量 不得超过200条
        :return:
        """
        params = {
            "mac": mac,
            "start_time": start_time,
            "end_time": end_time,
            "timestamp": timestamp or int(time.time() * 1000),
        }
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        return await self.send_request(
            "GET",
            f"https://{self._api_endpoint}/v1/apis/devices/events",
            params=params,
        )

    async def change_settings(
        self,
        mac: List[str],
        report_interval: int,
        collect_interval: int,
        timestamp: int = None,
    ):
        """
        修改设备配置
        :param mac: 需要获取信息的设备 MAC 列表
        :param report_interval: 上报周期(秒)最小为10s,且为采集周期的整数倍
        :param collect_interval: 采集周期(秒)
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        return await self.send_request(
            "PUT",
            f"https://{self._api_endpoint}/v1/apis/devices/settings",
            json={
                "mac": mac,
                "report_interval": report_interval,
                "collect_interval": collect_interval,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )

    async def add_alert(
        self, mac: str, alert_config: AlertConfig, timestamp: int = None
    ):
        return await self.send_request(
            "POST",
            f"https://{self._api_endpoint}/v1/apis/devices/settings/alert",
            json={
                "mac": mac,
                "alert_config": alert_config,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )

    async def get_alert(self, mac: str, timestamp: int = None) -> GetAlertResponse:
        return await self.send_request(
            "GET",
            f"https://{self._api_endpoint}/v1/apis/devices/settings/alert",
            params={
                "mac": mac,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )

    async def change_alert(
        self, mac: str, alert_config: AlertConfig, timestamp: int = None
    ):
        """
        修改报警配置
        :param mac:
        :param alert_config: 需要有配置id
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        return await self.send_request(
            "PUT",
            f"https://{self._api_endpoint}/v1/apis/devices/settings/alert",
            json={
                "mac": mac,
                "alert_config": alert_config,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )

    async def delete_alert(self, mac: str, config_id: List[int], timestamp: int = None):
        """
        删除报警配置
        :param mac:
        :param config_id:
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        return await self.send_request(
            "DELETE",
            f"https://{self._api_endpoint}/v1/apis/devices/settings/alert",
            json={
                "mac": mac,
                "config_id": config_id,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )

    async def get_groups(self, timestamp: int = None) -> GetGroupsResponse:
        """
        分组列表
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        return await self.send_request(
            "GET",
            f"https://{self._api_endpoint}/v1/apis/groups",
            params={"timestamp": timestamp or int(time.time() * 1000)},
        )

    async def get_device_info(
        self, mac_list: List[str], profile: List[str], timestamp: int = None
    ) -> DeviceInfoResponse:
        """
        获取设备的基本信息，如 SN 等
        :param mac_list: 设备 MAC
        :param profile: 需要获取的设备基本信息字段列表（参考 规范说明） e.g. ["sn", "customization.sn"],
        :param timestamp: 毫秒级时间戳(13位) 20s内有效,同一个请求不可重复
        :return:
        """
        return await self.send_request(
            "POST",
            f"https://{self._api_endpoint}/v1/apis/devices/profile/query",
            json={
                "macList": mac_list,
                "profile": profile,
                "timestamp": timestamp or int(time.time() * 1000),
            },
        )
