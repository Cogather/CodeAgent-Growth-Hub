"""网络区域权限配置"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from app.models import PermZoneBlue, PermZoneGreen, PermZoneYellow


@dataclass(frozen=True)
class ZoneConfig:
    key: str
    label: str
    model_hint: str
    model_class: Type


ZONES: dict[str, ZoneConfig] = {
    "yellow": ZoneConfig(
        key="yellow",
        label="黄区",
        model_hint="如：gpt-4o-mini, claude-3-haiku",
        model_class=PermZoneYellow,
    ),
    "blue": ZoneConfig(
        key="blue",
        label="蓝区",
        model_hint="如：gpt-4o, claude-3-opus",
        model_class=PermZoneBlue,
    ),
    "green": ZoneConfig(
        key="green",
        label="绿区",
        model_hint="如：gpt-4o, claude-3-5-sonnet",
        model_class=PermZoneGreen,
    ),
}


def get_zone(zone: str) -> ZoneConfig:
    cfg = ZONES.get(zone)
    if not cfg:
        raise KeyError(zone)
    return cfg
