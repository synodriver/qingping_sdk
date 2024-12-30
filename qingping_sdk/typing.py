# -*- coding: utf-8 -*-
from typing import List, Optional, TypedDict


# {'access_token': 'xxx',
# 'expires_in': 7199,
# 'scope':  'device_full_access',
# 'token_type': 'bearer'}
class GetAccessTokenResponse(TypedDict):
    access_token: str
    refresh_token: Optional[str]
    expires_in: int
    scope: str
    token_type: str


class DeviceStatus(TypedDict):
    offline: Optional[bool]  # 状态 （True表示离线False表示在线）


class DeviceProduct(TypedDict):
    id: Optional[
        str
    ]  # 产品id https://developer.qingping.co/cloud-to-cloud/specification-guidelines#21-%E4%BA%A7%E5%93%81%E5%88%97%E8%A1%A8
    name: Optional[str]  # 产品名称
    en_name: Optional[str]  # 产品英文名称
    code: Optional[str]
    noBleSetting: Optional[bool]


class DeviceSetting(TypedDict):
    report_interval: Optional[int]  # 设备数据上报间隔（秒）
    collect_interval: Optional[int]  # 设备数据采集间隔（秒）


class DeviceInfo(TypedDict):
    name: str  # 设备名称
    mac: str  #  设备mac地址
    group_id: str  # 分组id
    group_name: str  # 分组名称
    status: Optional[DeviceStatus]  # 状态
    connection_type: Optional[str]  # WIFI
    version: str  # 设备版本
    created_at: str  # 设备注册时间
    product: DeviceProduct  # 产品信息
    setting: DeviceSetting  # 设备上报配置


class DataDetail(TypedDict):
    value: Optional[float]  # 数据值
    level: Optional[float]  # 等级
    status: Optional[float]  # 状态


class DeviceData(TypedDict):
    battery: Optional[DataDetail]  # 电量
    signal: Optional[DataDetail]  # undocumented，但是实际返回的有
    humidity: Optional[DataDetail]  # 湿度
    pressure: Optional[DataDetail]  # 气压
    temperature: Optional[DataDetail]  # 温度
    tvoc: Optional[DataDetail]  # 挥发物质
    co2: Optional[DataDetail]  # 二氧化碳
    pm25: Optional[DataDetail]  # pm2.5
    timestamp: Optional[DataDetail]  # 时间


class Device(TypedDict):
    info: DeviceInfo  # 设备信息
    data: Optional[DeviceData]  # 设备数据


class DeviceResponse(TypedDict):
    total: int  # 设备总数
    devices: List[Device]  # 设备数据


class HistoryDataResponse(TypedDict):
    total: int  # 总条数
    data: List[DeviceData]  # 数据正文


class AlertConfig(TypedDict):
    id: Optional[int]  # 配置id 仅仅在get_alert的返回值中
    metric_name: str  # 事件属性（温度、湿度、气压等）
    # （温度：temperature，湿度：humidity）
    operator: str  # 操作符（大于gt、小于lt）
    threshold: float  # 阈值


class Event(TypedDict):
    data: Optional[DeviceData]  # 设备数据
    alert_config: Optional[AlertConfig]  # 触发条件


class HistoryEventResponse(TypedDict):
    total: int  # 总条数
    events: List[Event]  # 数据正文


class GetAlertResponse(TypedDict):
    mac: str
    alert_configs: List[AlertConfig]


class Group(TypedDict):
    id: int  # 分组id
    name: str  # 分组名称


class GetGroupsResponse(TypedDict):
    total: int  # 分组总数
    groups: List[Group]  # 数据正文


class Profile(TypedDict):
    mac: str  # 设备 MAC
    ble_mac: Optional[str]  # ble.mac undocumented但是返回值有
    sn: Optional[str]  # 青萍 SN
    customization_sn: Optional[str]  # customization.sn 自定义 SN


class DeviceInfoResponse(TypedDict):
    total: int  # 总条数
    profiles: List[Profile]  # 数据正文
