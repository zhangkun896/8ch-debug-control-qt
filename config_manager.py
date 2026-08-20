"""
8通道调试控制系统 - 配置管理模块
负责 config.json 的读写与校验
"""
import json
from pathlib import Path

# 配置文件与 main.py 同级
CONFIG_PATH = Path(__file__).parent / "config.json"

EMPTY_TEMPLATE: dict = {
    "serial": {"port": "", "baudrate": 115200},
    "global_settings": {
        "channels": [
            {"ch_id": i, "name": "", "current": "", "max": "", "min": "", "step": ""}
            for i in range(8)
        ]
    },
    "modes": [],
    "global_command_template": "SET CH{n}={val}\n",
}


def _normalize_mode(mode: dict) -> dict:
    """确保每个模式都有完整字段"""
    if "locked_values" not in mode:
        mode["locked_values"] = [""] * 8
    if "limits" not in mode:
        mode["limits"] = [
            {"max": None, "min": None, "step": None} for _ in range(8)
        ]
    if "mcu_limit" not in mode:
        mode["mcu_limit"] = {"max": None, "min": None}
    if "command_template" not in mode:
        mode["command_template"] = None
    return mode


def _normalize_channel(ch: dict) -> dict:
    """确保每个通道都有完整字段"""
    for key in ("name", "current", "max", "min", "step"):
        if key not in ch:
            ch[key] = ""
    return ch


def _normalize_config(config: dict) -> dict:
    """确保配置结构完整"""
    config.setdefault("modes", [])
    config.setdefault("global_command_template", "SET CH{n}={val}\\n")
    config.setdefault("serial", {"port": "", "baudrate": 115200})
    gs = config.setdefault("global_settings", {})
    gs.setdefault("channels", [])
    for mode in config["modes"]:
        _normalize_mode(mode)
    for ch in gs["channels"]:
        _normalize_channel(ch)
    return config


def load_config() -> dict:
    """读取配置文件，不存在则用空模板创建"""
    if not CONFIG_PATH.exists():
        save_config(EMPTY_TEMPLATE)
        return _normalize_config(EMPTY_TEMPLATE.copy())
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return _normalize_config(config)


def save_config(config: dict) -> None:
    """保存配置到 JSON 文件"""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
