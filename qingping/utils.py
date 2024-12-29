# -*- coding: utf-8 -*-
"""
Copyright (c) 2008-2024 synodriver <diguohuangjiajinweijun@gmail.com>
"""
from base64 import b64encode


def create_auth(app_key: str, app_secret: str) -> str:
    return b64encode(app_key.encode() + b":" + app_secret.encode()).decode()
